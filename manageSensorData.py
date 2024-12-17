import json
import gspread
from google.oauth2.service_account import Credentials
import paho.mqtt.client as mqtt
# Path to your service account key JSON file
SERVICE_ACCOUNT_FILE = "raspberrypiconnection-bc2443a6ce6d.json"
# Define the scope for Google Sheets and Drive APIs
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
# Authenticate using the service account key
def connect_to_sheet(sheet_name):
    # Create credentials using the service account file
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # Authorize the gspread client with these credentials
    client = gspread.authorize(credentials)
    
    # Open the Google Sheet by name
    sheet = client.open(sheet_name).sheet1  # Access the first sheet
    return sheet
# Send data to the Google Sheet
def send_data_to_sheet(data):
    try:
        sheet = connect_to_sheet(SHEET_NAME)
        sheet.append_row(data)  # Append data as a new row
        print("Data successfully sent to Google Sheet!")
    except Exception as e:
        print("An error occurred:", e)
# Callback to handle received messages
def on_message(client, userdata, message):
    print(f"Received: {message.payload.decode()}")
    msg_payload = json.loads(message.payload.decode())
    data_to_send = [msg_payload["sensorID"],msg_payload["fillLevel"],msg_payload["timestamp"]]
    send_data_to_sheet(data_to_send)
if __name__ == "__main__":
    # Replace with your Google Sheet name
    SHEET_NAME = "SmartWasteManagementSystem"
    
    # Setup MQTT Client
    client = mqtt.Client()
    client.on_message = on_message
    # Connect to MQTT broker
    client.connect("192.168.149.196", 1883, 60)
    client.subscribe("sensors/ultrasonic")
    # Start listening for messages
    client.loop_forever()

