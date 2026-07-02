from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks'
]

flow = InstalledAppFlow.from_client_secrets_file('google_credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

with open('google_token.json', 'w') as f:
    f.write(creds.to_json())

print("✅ Token generado correctamente!")