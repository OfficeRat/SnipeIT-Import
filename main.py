import db
import api
import time
import requests
import threading
from datetime import datetime
from dotenv import dotenv_values


db.create_db()
env_values = dotenv_values('.env')
SLACK_WEBHOOK_URL = env_values.get("SLACK_URL") 
SNIPE_URL = env_values.get("SNIPE_URL")
SUPPORTED_DEVICE_PREFIX = env_values.get("DEVICE_PREFIX").split(",") 


print(f"{datetime.now()} Starting import")

start_time = time.time()

snipe_devices = [device['name'] for device in api.snipe_get('hardware?limit=500')]
snipe_devices_users = api.snipe_get('hardware?limit=999')
model_id = {model['name']: model['id'] for model in api.snipe_get("models")}
user_id = {user['username']: user['id'] for user in api.snipe_get("users?limit=200")}
device_id = {device['asset_tag']: device['id'] for device in api.snipe_get("hardware?limit=500")}
manufacturer_id = {manufacturer['name'].lower(): manufacturer['id'] for manufacturer in api.snipe_get("manufacturers")}

devices = api.managed_devices()
model_lock = threading.Lock()

def send_slack_message(message):
    payload = {
        "text": message,
    }
    response = requests.post(url=SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print(f"Failed to send Slack message: {response.text}")

def check_and_create_snipe_manufacturer(name):
    check_manufacturer = db.use_db("get manufacturer", name)
    if check_manufacturer == None:
        for manufacturer_name in manufacturer_id:
            db.use_db("create manufacturer", manufacturer_name, manufacturer_id.get(manufacturer_name.lower()))
        check_manufacturer = db.use_db("get manufacturer", name)
        if check_manufacturer == None:
            payload = {
                "name": name
            }
            result = api.snipe_post("manufacturers", payload).json()
            manufacturer = {manufacturer['name']: manufacturer['id'] for manufacturer in api.snipe_get("manufacturers")}
            db.use_db("create manufacturer", name, manufacturer.get(name.lower()))
            return
    elif check_manufacturer != None:
        return

def create_snipe_model(modelName):
    existing_model = db.use_db('get model', modelName)
    manufacturerID = db.use_db('get manufacturer', existing_model[3])
    if existing_model[2] == None:
        payload ={
            "name": modelName,
            "category_id": 2,
            "manufacturer_id": manufacturerID[2]
        }
        api.snipe_post("models", payload)

def create_device(name, modelID, serialNumber):
    if name not in snipe_devices:
        payload = {
            "asset_tag": name,
            "status_id": 2,
            "model_id": modelID,
            "name": name,
            "serial": serialNumber
        }
        #print(payload)    
        api.snipe_post("hardware", payload)
        device_id = {device['asset_tag']: device['id'] for device in api.snipe_get("hardware?limit=500")}
        device = device_id.get(name)
        message = f'<{SNIPE_URL}/hardware/{device}|{name}> har blitt lagt til'
        send_slack_message(message)

def process_device_info(row):
    with model_lock:    
        # 0 = ID, 1 = Asset tag / Device name, 2 = Serial Number, 3 = Model, 4 = Model ID , 5 = Manufacturer, 6 = Manufacturer ID
        
        check_and_create_snipe_manufacturer(row[5])

        create_snipe_model(row[3])

        if row[1] not in snipe_devices:
            model_id = db.use_db('get model', row[3])
            create_device(row[1],model_id[2], row[2])
    

# FILL DATABASE
for manufacturer in devices:
    if SUPPORTED_DEVICE_PREFIX[0] in manufacturer['deviceName'] or SUPPORTED_DEVICE_PREFIX[1] in manufacturer['deviceName']:
        db.use_db("create manufacturer", manufacturer['manufacturer'], manufacturer_id.get(manufacturer['manufacturer'].lower()))

for model in devices:
    if SUPPORTED_DEVICE_PREFIX[0] in model['deviceName'] or SUPPORTED_DEVICE_PREFIX[1] in model['deviceName']:
        db.use_db("create model", model['model'], model_id.get(model['model']), model['manufacturer'], manufacturer_id.get(model['manufacturer'].lower()))

for device in devices:
    if SUPPORTED_DEVICE_PREFIX[0] in device['deviceName'] or SUPPORTED_DEVICE_PREFIX[1] in device['deviceName']:
        db.use_db("create device",device['deviceName'], device['serialNumber'], device['model'], model_id.get(device['model']), device['manufacturer'],manufacturer_id.get(device['manufacturer'].lower()) )

for device in snipe_devices_users:
    if device['assigned_to']:
        if device['assigned_to']['type'] == 'location':
            continue
        elif device['category']['name'] == "PC":
            db.use_db('create snipe_users', device['asset_tag'], device['assigned_to']['username'], user_id.get(device['assigned_to']['username'])) 
    
for user in devices:
    if SUPPORTED_DEVICE_PREFIX[0] in user['deviceName'] or SUPPORTED_DEVICE_PREFIX[1] in user['deviceName']:
        db.use_db("create intune_users", user['userPrincipalName'], user_id.get(user['userPrincipalName']), user['deviceName'])



num_threads = 20

threads = []
print(f"{datetime.now()} Importing")
device_count = db.use_db('get device count')
for row in device_count:
    thread = threading.Thread(target=process_device_info, args=(row,))
    thread.start()
    threads.append(thread)
    if len(threads) >= num_threads:
        for thread in threads:
            thread.join()
        threads = []

for thread in threads:
    thread.join()

print(f"{datetime.now()} Done importing")

def assigned_to_user(device):
    if SUPPORTED_DEVICE_PREFIX[0] in device or SUPPORTED_DEVICE_PREFIX[1] in device:
        snipe_user = db.use_db('get snipe user', device)
        intune_user = db.use_db('get intune user', device)

        
        if snipe_user == None:
            if intune_user[0] != '':
                payload = {
                    'status_id': 5,
                    'assigned_user': intune_user[1],
                    'checkout_to_type': "user"
                }
                response = api.snipe_post(f'hardware/{device_id.get(device)}/checkout', payload)
                if response == 200:
                    db.use_db(f'DELETE FROM snipe_users WHERE device = {device}')
                    print(f'Updated {device}')
                    return
                    
            return
        
        if snipe_user[0] != intune_user[0]:
            if intune_user[0] == '': 
                if api.snipe_device_user(device_id.get(device))['status_label']['id'] == 7: # STATUS 7 ER UTLÅN
                    return
                else:
                    payload = {
                        'status_id': 2
                    }
                    response = api.snipe_post(f'hardware/{device_id.get(device)}/checkin', payload)
                    db.use_db('delete',f'DELETE FROM snipe_users WHERE device = {device} ')
                    if response.status_code == 200:
                        print(f'Checked in {device}')
                    return
            
            payload = {
                'status_id': 5,
                'assigned_to': intune_user[1],
            }
            #print(device_id.get(device))
            
            response = api.snipe_patch(f'hardware/{device_id.get(device)}', payload)
            message = f'<{SNIPE_URL}/hardware/{device_id.get(device)}|{device}> Er tildelt {intune_user[0]} (PATCH)'
            send_slack_message(message)
            print(f'Patched/Checked out {device}')
            return
            
                


print(f"{datetime.now()} Starting update")
threads = []
for device in devices:
    thread = threading.Thread(target=assigned_to_user, args=(device['deviceName'],))
    thread.start()
    threads.append(thread)
    if len(threads) >= num_threads:
        for thread in threads:
            thread.join()
        threads = []

for thread in threads:
    thread.join()

print(f"{datetime.now()} Done updating")

end_time = time.time()
print(end_time - start_time)
print(f'''\nSnipe api count:      {api.snipe_api_counter() - 1} \nMicrosoft api count:  {api.microsoft_api_counter() - 1} \ntotal api count:      {(api.microsoft_api_counter() + api.snipe_api_counter())-4}''')
