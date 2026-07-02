from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_calendar():
    creds = Credentials.from_authorized_user_file('google_token.json')
    return build('calendar', 'v3', credentials=creds)

def get_tasks():
    creds = Credentials.from_authorized_user_file('google_token.json')
    return build('tasks', 'v1', credentials=creds)