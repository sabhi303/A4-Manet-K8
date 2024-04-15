"""
Name: Abhijit Somnath Shendage
Student ID: 123103499
"""

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# SQLite database connection
conn = sqlite3.connect('cloudlet.db', check_same_thread=False)
c = conn.cursor()

# Create table for devices if not exists
c.execute('''CREATE TABLE IF NOT EXISTS devices
             (id INTEGER PRIMARY KEY AUTOINCREMENT, device_type TEXT, username TEXT, password TEXT)''')

# Create table for MANETs if not exists
c.execute('''CREATE TABLE IF NOT EXISTS manets
             (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT)''')

# Create table for MANET members if not exists
c.execute('''CREATE TABLE IF NOT EXISTS manet_members
             (manet_id INTEGER, device_id INTEGER,
             FOREIGN KEY(manet_id) REFERENCES manets(id),
             FOREIGN KEY(device_id) REFERENCES devices(id))''')


# Commit changes
conn.commit()


@app.route('/check_if_alive', methods=['GET'])
def check_if_alive():
    return jsonify({'message': 'I am alive!'})

@app.route('/clear_database', methods=['GET'])
def clear_database_tables():

    c.execute('''DELETE FROM manet_members''')
    c.execute('''DELETE FROM manets''')
    c.execute('''DELETE FROM devices''')
    # commit
    conn.commit()
    return jsonify({'message': 'Truncate successful!'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    device_type = data['device_type']
    username = data['username']
    password = data['password']

    print("Device Type", device_type)
    print("username", username)
    print("password", password)

    # Insert device info into database
    c.execute("INSERT INTO devices (device_type, username, password) VALUES (?, ?, ?)", (device_type, username, password))
    conn.commit()
    device_id = c.lastrowid
    
    return jsonify({'device_id': device_id})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    # Check if username and password match
    c.execute("SELECT * FROM devices WHERE username=? AND password=?", (username, password))
    device = c.fetchone()
    if device:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Login failed'}), 401


@app.route('/create_manet', methods=['POST'])
def create_manet():
    data = request.get_json()
    net_type = data['manet_type']
    
    # Insert MANET info into database
    c.execute("INSERT INTO manets (type) VALUES (?)", (net_type,))
    conn.commit()
    manet_id = c.lastrowid
    
    return jsonify({'manet_id': manet_id})


@app.route('/join_manet', methods=['POST'])
def join_manet():
    data = request.get_json()
    manet_id = data['manet_id']
    device_id = data['device_id']
    
    # Insert device into MANET members
    c.execute("INSERT INTO manet_members (manet_id, device_id) VALUES (?, ?)", (manet_id, device_id))
    conn.commit()
    
    return jsonify({'message': 'Joined MANET successfully'})


@app.route('/leave_manet', methods=['POST'])
def leave_manet():
    data = request.get_json()
    device_id = data['device_id']
    
    # Remove device from MANET members
    c.execute("DELETE FROM manet_members WHERE device_id=?", (device_id,))
    conn.commit()
    
    return jsonify({'message': 'Left MANET successfully'})


@app.route('/split_manet', methods=['POST'])
def split_manet():
    data = request.get_json()
    manet_id = data['manet_id']
    net_type = data['net_type']

    # Insert MANET info into database
    c.execute("INSERT INTO manets (type) VALUES (?)", (net_type,))
    conn.commit()
    new_manet_id = c.lastrowid
    
    return jsonify({'message': 'Split Successful', 'new_manet_id': new_manet_id})

@app.route('/get_devices_in_manet', methods=['POST'])
def get_devices_in_manet():
    data = request.get_json()
    manet_id = data['manet_id']
    
    c.execute("SELECT device_id FROM manet_members WHERE manet_id=?", (str(manet_id),))
    result = c.fetchall()
    # Assuming new MANET IDs
    # here I will get devices in this manet
    
    return jsonify({'message': 'Fetch successful', 'devices_on_manet': result})


@app.route('/merge_manets', methods=['POST'])
def merge_manets():
    data = request.get_json()
    manet_id_1 = data['manet_id_1']
    manet_id_2 = data['manet_id_2']
    c.execute("DELETE FROM manets WHERE id=?", (str(manet_id_2),))
    c.execute("DELETE FROM manet_members WHERE manet_id=?", (str(manet_id_2),))
    conn.commit()
    return jsonify({'message': f'Merge successful'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)