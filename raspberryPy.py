import time
import RPi.GPIO as GPIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# GPIO Pin Configuration
GPIO.setmode(GPIO.BCM)
TRIG = 18
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Google Drive and Sheets Setup
CREDENTIALS_FILE = 'credentials.json'  # Path to your OAuth credentials
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

# Google Sheets Configuration
SPREADSHEET_ID = 'your_google_sheet_id_here'  # Replace with your Google Sheet ID
SHEET_RANGE = 'Sheet1!A:B'  # Assuming data is logged in columns A and B

def read_distance():
    """Reads distance from HC-SR04 sensor."""
    GPIO.output(TRIG, False)
    time.sleep(2)  # Allow sensor to settle
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10 µs pulse
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound: 34300 cm/s
    return round(distance, 2)

def upload_to_drive(file_path, drive_service):
    """Uploads a file to Google Drive."""
    file_metadata = {'name': 'SensorData.txt'}
    media = MediaFileUpload(file_path, mimetype='text/plain')
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media).execute()
    return uploaded_file['id']

def append_to_google_sheet(data, sheet_service):
    """Appends data to a Google Sheet."""
    sheet_service.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_RANGE,
        valueInputOption='RAW',
        body={'values': [data]}
    ).execute()

def main():
    # Authenticate with Google APIs
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SPREADSHEET_ID)
    sheet_service = build('sheets', 'v4', credentials=creds).spreadsheets()
    
    while True:
        distance = read_distance()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp} - Distance: {distance} cm")
        
        # Log to a local file
        file_path = '/home/pi/SensorData.txt'
        with open(file_path, 'a') as file:
            file.write(f"{timestamp}, {distance} cm\n")
        
        # Upload the file to Google Drive
        upload_to_drive(file_path, drive_service)
        
        # Append data to Google Sheets
        append_to_google_sheet([timestamp, distance], sheet_service)
        
        # Wait for an hour before the next read
        time.sleep(3600)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting Program")
    finally:
        GPIO.cleanup()

