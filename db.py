import sqlite3

def create_db():
    conn = sqlite3.connect('buffer.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS manufacturers (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        manufacturer_id INTEGER
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS models (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        model_id INTEGER,
        manufacturer TEXT,
        manufacturer_id INTEGER,
        FOREIGN KEY (manufacturer) REFERENCES manufacturers(name),
        FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY,
        device TEXT,
        serial TEXT UNIQUE,
        model TEXT,
        model_id INTEGER,
        manufacturer TEXT,
        manufacturer_id INTEGER,
        FOREIGN KEY (model) REFERENCES models(name),
        FOREIGN KEY (model_id) REFERENCES models(model_id)
        FOREIGN KEY (manufacturer) REFERENCES manufacturers(name),
        FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS snipe_users(
        user TEXT,
        user_id INTEGER,
        device TEXT UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS intune_users(
        user TEXT,
        user_id INTEGER,
        device text UNIQUE
    )
    ''')
    conn.commit()
    conn.close()

def snipe_users(cursor, device, username, user_id):
    cursor.execute('INSERT OR REPLACE INTO snipe_users (user, user_id, device) VALUES (?, ?, ?)', 
                  (username, user_id, device))

def intune_users(cursor, username, user_id, device):
    cursor.execute('INSERT OR REPLACE INTO intune_users (user, user_id, device) VALUES (?, ?, ?)', 
                  (username, user_id, device))

def create_manufacturer(cursor, name, manufacturer_id):
    cursor.execute('INSERT OR IGNORE INTO manufacturers (name, manufacturer_id) VALUES (?, ?)', 
                  (name, manufacturer_id))

def create_model(cursor, name, model_id, manufacturer, manufacturer_id):
    cursor.execute('INSERT OR IGNORE INTO models (name, model_id, manufacturer, manufacturer_id) VALUES (?, ?, ?, ?)', 
                  (name, model_id, manufacturer, manufacturer_id))

def create_device(cursor, device, serial, model, model_id, manufacturer, manufacturer_id):
    cursor.execute('INSERT OR IGNORE INTO devices (device, serial, model, model_id, manufacturer, manufacturer_id) VALUES (?, ?, ?, ?, ?, ?)',
                  (device, serial, model, model_id, manufacturer, manufacturer_id))

def get_manufacturer(cursor, name):
    cursor.execute('SELECT * FROM manufacturers WHERE name = ?', (name,))
    return cursor.fetchone()

def get_model(cursor, model):
    cursor.execute('SELECT * FROM models WHERE name = ?', (model,))
    return cursor.fetchone()

def get_device(cursor, device_id):
    cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
    return cursor.fetchone()

def get_device_count(cursor):
    cursor.execute('SELECT * FROM devices')
    return cursor.fetchall()

def get_count(cursor, table):
    cursor.execute(f'SELECT COUNT(*) FROM {table};')
    return cursor.fetchone()

def get_snipe_user(cursor, device):
    cursor.execute('SELECT * FROM snipe_users where device = ?', (device,))
    return cursor.fetchone()

def get_intune_user(cursor, device):
    cursor.execute('SELECT * FROM intune_users where device = ?', (device,))
    return cursor.fetchone()
def delete(cursor, command):
    cursor.execute(f'{command}')
    return cursor.fetchone()

def use_db(statement, *args):
    conn = sqlite3.connect('buffer.sqlite')
    cursor = conn.cursor()

    operations = {
        "create manufacturer": create_manufacturer,
        "create model": create_model,
        "create device": create_device,
        "create snipe_users": snipe_users,
        "create intune_users": intune_users,
        "get manufacturer": get_manufacturer,
        "get model": get_model,
        "get device": get_device,
        "get device count": get_device_count,
        "get count": get_count,
        "get snipe user": get_snipe_user,
        "get intune user": get_intune_user,
        "delete": delete
    }

    operation_func = operations.get(statement)
    if operation_func:
        result = operation_func(cursor, *args)
        conn.commit()
        conn.close()
        return result
    else:
        print('Error, you didn\'t give a valid statement')
