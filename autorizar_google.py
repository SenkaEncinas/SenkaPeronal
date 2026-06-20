from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks',
]

print("Iniciando flujo OAuth...")

flow = InstalledAppFlow.from_client_secrets_file('google_credentials.json', SCOPES)

print("Abriendo navegador...")
creds = flow.run_local_server(port=8080, open_browser=True)

print("Guardando token...")
with open('google_token.json', 'w') as f:
    f.write(creds.to_json())

print("✅ Token guardado en google_token.json")