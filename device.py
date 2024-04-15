"""
Name: Abhijit Somnath Shendage
Student ID: 123103499
"""

import requests


# Function to send HTTP requests to the cloudlet
def send_request(cloudlet_url, endpoint, data, request_type="POST"):
    url = f"{cloudlet_url}/{endpoint}"
    if request_type == "POST":
        response = requests.post(url, json=data)
    else:
        response = requests.get(url)
    return response.json()


class Device:
    type: str

    def __init__(self, device_type):
        # assigning None values initially
        self.username = None
        self.net_id = None
        self.type = device_type

    def register(self, username, password, cloudlet_connection_details):

        self.username = username
        self.password = password
        register_data = {
            "device_type": self.type,
            "username": self.username,
            "password": self.password,
        }

        #
        device_id = send_request(
            cloudlet_connection_details, "register", register_data
        )["device_id"]
        if device_id:
            self.device_id = device_id
            return device_id
        else:
            return False

    def login(self, username, password, cloudlet_connection_details):
        login_data = {"username": username, "password": password}
        response = send_request(cloudlet_connection_details, "login", login_data)

        return response["message"]

    def join_network(self, net_id, cloudlet_connection_details):
        join_data = {"manet_id": net_id, "device_id": self.device_id}
        response = send_request(cloudlet_connection_details, "join_manet", join_data)

        return response["message"]

    def leave_network(self,  cloudlet_connection_details):
        leave_data = {"device_id": self.device_id}
        response = send_request(cloudlet_connection_details,"leave_manet", leave_data)
        return response["message"]
