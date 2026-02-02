import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import CONFIG

def get_gmail_service():
    """Authenticate with Google and return the Gmail service."""
    creds = None
    if os.path.exists(CONFIG['TOKEN_FILE']):
        creds = Credentials.from_authorized_user_file(CONFIG['TOKEN_FILE'], CONFIG['SCOPES'])
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CONFIG['CREDENTIALS_FILE'], CONFIG['SCOPES'])
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Authentication failed: {e}")
                print(f"Ensure {CONFIG['CREDENTIALS_FILE']} is present and correct.")
                return None
                
        with open(CONFIG['TOKEN_FILE'], 'w') as token:
            token.write(creds.to_json())
            
    return build('gmail', 'v1', credentials=creds)
