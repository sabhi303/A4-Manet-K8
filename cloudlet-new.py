from flask import Flask, request, jsonify
import sys
import mysql.connector

app = Flask(__name__)

# MySQL database connection
conn = mysql.connector.connect(
    host=f"{sys.argv[1]}",
    user='root',
    password='password',
)

# Create the database if it doesn't exist
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS manet")
conn.commit()
cursor.close()

# Now connect to the manet database
conn = mysql.connector.connect(
    host=f"{sys.argv[1]}",
    user='root',
    password='password',
    database='manet'
)

cursor = conn.cursor(buffered=True)

# Create table for devices if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS devices
             (id INT AUTO_INCREMENT PRIMARY KEY, device_type VARCHAR(255), username VARCHAR(255), password VARCHAR(255))''')

# Create table for MANETs if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS manets
             (id INT AUTO_INCREMENT PRIMARY KEY, type VARCHAR(255))''')

# Create table for MANET members if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS manet_members
             (manet_id INT, device_id INT,
             FOREIGN KEY(manet_id) REFERENCES manets(id) ON DELETE CASCADE,
             FOREIGN KEY(device_id) REFERENCES devices(id) ON DELETE CASCADE)''')

@app.route('/check_if_alive', methods=['GET'])
def check_if_alive():
    return jsonify({'message': 'I am alive!'})

@app.route('/clear_database', methods=['GET'])
def clear_database_tables():
    try:
        cursor.execute('''DELETE FROM manet_members''')
        cursor.execute('''DELETE FROM manets''')
        cursor.execute('''DELETE FROM devices''')
        conn.commit()
        return jsonify({'message': 'Truncate successful!'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    device_type = data['device_type']
    username = data['username']
    password = data['password']

    cursor.execute("INSERT INTO devices (device_type, username, password) VALUES (%s, %s, %s)", (device_type, username, password))
    conn.commit()
    device_id = cursor.lastrowid
    
    return jsonify({'device_id': device_id})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    cursor.execute("SELECT * FROM devices WHERE username=%s AND password=%s", (username, password))
    device = cursor.fetchone()
    if device:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Login failed'}), 401

@app.route('/create_manet', methods=['POST'])
def create_manet():
    data = request.get_json()
    net_type = data['manet_type']
    
    # Insert MANET info into database
    cursor.execute("INSERT INTO manets (type) VALUES (%s)", (net_type,))
    conn.commit()
    manet_id = cursor.lastrowid
    
    return jsonify({'manet_id': manet_id})

@app.route('/join_manet', methods=['POST'])
def join_manet():
    data = request.get_json()
    manet_id = data['manet_id']
    device_id = data['device_id']
    
    # Insert device into MANET members
    cursor.execute("INSERT INTO manet_members (manet_id, device_id) VALUES (%s, %s)", (manet_id, device_id))
    conn.commit()
    
    return jsonify({'message': 'Joined MANET successfully'})

@app.route('/leave_manet', methods=['POST'])
def leave_manet():
    data = request.get_json()
    device_id = data['device_id']
    
    # Remove device from MANET members
    cursor.execute("DELETE FROM manet_members WHERE device_id=%s", (device_id,))
    conn.commit()
    
    return jsonify({'message': 'Left MANET successfully'})

@app.route('/split_manet', methods=['POST'])
def split_manet():
    data = request.get_json()
    manet_id = data['manet_id']
    net_type = data['net_type']

    # Insert MANET info into database
    cursor.execute("INSERT INTO manets (type) VALUES (%s)", (net_type,))
    conn.commit()
    new_manet_id = cursor.lastrowid
    
    return jsonify({'message': 'Split Successful', 'new_manet_id': new_manet_id})

@app.route('/get_devices_in_manet', methods=['POST'])
def get_devices_in_manet():
    data = request.get_json()
    manet_id = data['manet_id']
    
    cursor.execute("SELECT device_id FROM manet_members WHERE manet_id=%s", (manet_id,))
    result = cursor.fetchall()
    
    return jsonify({'message': 'Fetch successful', 'devices_on_manet': result})

@app.route('/merge_manets', methods=['POST'])
def merge_manets():
    data = request.get_json()
    manet_id_1 = data['manet_id_1']
    manet_id_2 = data['manet_id_2']
    
    try:
        # Move members from manet_id_2 to manet_id_1
        cursor.execute("UPDATE manet_members SET manet_id = %s WHERE manet_id = %s", (manet_id_1, manet_id_2))
        
        # Delete manet_id_2
        cursor.execute("DELETE FROM manets WHERE id = %s", (manet_id_2,))
        
        conn.commit()
        
        return jsonify({'message': 'Merge successful'})
    except mysql.connector.Error as err:
        # Handle any errors that occur during the database operation
        return jsonify({'error': str(err)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
