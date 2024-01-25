from dotenv import dotenv_values
import requests

env_values = dotenv_values('.env')
snipe_api = env_values.get('SNIPE_API_KEY')
client_id = env_values.get('MICROSOFT_CLIENT_ID')
client_secret= env_values.get('MICROSOFT_CLIENT_SECRET')
snipe_url = env_values.get('SNIPE_API_URL')
microsoft_url = env_values.get('MICROSOFT_URL')

accept = 'application/json'
snipe_api_count = 0
microsoft_api_count = 0

def snipe_api_counter():
    global snipe_api_count
    snipe_api_count += 1
    return snipe_api_count

def microsoft_api_counter():
    global microsoft_api_count
    microsoft_api_count += 1
    return microsoft_api_count

# Microsoft api token generation
def token():
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "resource": "https://graph.microsoft.com"
    }
    response = requests.post(microsoft_url, data=data)
    access_token = response.json()["access_token"]
    microsoft_api_counter()
    return access_token

# Microsoft Endpoint/Intune
def managed_devices():
    headers = {
        "Authorization": f"{token()} ",
        "Accept": accept
    }
    url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices?$top=9999"
    response = requests.get(url, headers=headers)
    managed_devices = response.json()["value"]
    microsoft_api_counter()
    return managed_devices

#intune alle annsatte
def users():
    url = 'https://graph.microsoft.com/v1.0/groups/2ccd361e-70c3-4b1d-ad26-cfa75b1720c1/members?$top=999'
    headers = {
        "Authorization": f"{token()} ",
        "Accept": accept
    }
    response = requests.get(url, headers=headers)
    users = response.json()["value"]
    microsoft_api_counter()
    return users

def user_device(user_id):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}/managedDevices'
    headers = {
        "Authorization": f"{token()} ",
        "Accept": accept
    }
    response = requests.get(url, headers=headers)
    user_device = response.json()["value"]
    microsoft_api_counter()
    return user_device

# Snipe Get request with the endpoint as a variable
def snipe_get(endpoint):
    headers = {
        "Authorization": f"{snipe_api}",
        "Accept": accept
    }
    response = requests.get(snipe_url+endpoint, headers=headers)
    snipe_assets = response.json()["rows"]
    snipe_api_counter()
    return snipe_assets

def snipe_device_user(deviceID):
    headers = {
        "Authorization": f"{snipe_api}",
        "Accept": accept
    }
    response = requests.get(snipe_url+'hardware/'+str(deviceID), headers=headers)
    snipe_assets = response.json()
    snipe_api_counter()
    return snipe_assets

def snipe_post(endpoint, payload):
    headers = {
        "Authorization": f"{snipe_api}",
        "Accept": accept
    }
    response = requests.post(snipe_url+endpoint, json=payload, headers=headers)
    snipe_api_counter()
    return response

def snipe_patch(endpoint, payload):
    headers = {
        "Authorization": f"{snipe_api}",
        "Accept": accept,
        "content-type": accept
    }
    response = requests.patch(snipe_url+endpoint, json=payload, headers=headers)
    snipe_api_counter()
    return response