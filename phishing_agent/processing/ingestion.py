import os.path
import base64
import time
from datetime import datetime
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .queue_manager import push_email_to_queue
import config

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

class GmailIngestor:
    def __init__(self):
        self.logger = logging.getLogger("PhishingAgent")
        self.creds = None
        self.service = None

    def authenticate(self):
        """
        Handles OAuth 2.0 authentication flow.
        """
        try:
            # The file token.json stores the user's access and refresh tokens.
            if os.path.exists(config.TOKEN_FILE):
                self.creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, SCOPES)
            
            # If there are no (valid) credentials available, let the user log in.
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.logger.info("Refreshing expired access token...")
                    self.creds.refresh(Request())
                else:
                    self.logger.info("No valid token found. Initiating OAuth flow...")
                    if not os.path.exists(config.CREDENTIALS_FILE):
                        self.logger.critical(f"CRITICAL: {config.CREDENTIALS_FILE} not found!")
                        self.logger.critical("You MUST download OAuth Client ID JSON from Google Cloud and save it as credentials.json")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        config.CREDENTIALS_FILE, SCOPES)
                    self.creds = flow.run_local_server(port=8080, open_browser=True)
                
                # Save the credentials for the next run
                with open(config.TOKEN_FILE, 'w') as token:
                    token.write(self.creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=self.creds)
            self.logger.info("Successfully authenticated with Gmail API.")
            return True

        except Exception as e:
            self.logger.error(f"Authentication Failed: {e}", exc_info=True)
            return False

    def fetch_emails(self, lookback_limit=10):
        """
        Fetches UNSEEN emails using Gmail API query `q='is:unread'`.
        Note: Gmail API automatically handles folders via labels.
        'is:unread' checks ALL mail (Inbox, etc) unless filtered.
        User wanted to exclude Spam/Trash explicitly?
        'is:unread -label:spam -label:trash'
        """
        if not self.service:
            if not self.authenticate():
                return

        try:
            self.logger.info("API: fetching unread emails...")
            # Query: unread, not spam, not trash
            query = 'is:unread -label:spam -label:trash'
            
            results = self.service.users().messages().list(userId='me', q=query, maxResults=lookback_limit).execute()
            messages = results.get('messages', [])

            if not messages:
                # self.logger.info("No new unread emails found.")
                return

            self.logger.info(f"API found {len(messages)} unread messages.")

            # Processing newest first? The list order depends on API. Usually it returns newest first.
            # We can verify or just process list.
            
            for msg in messages:
                self.process_single_email(msg['id'], msg['threadId'])
                
        except HttpError as error:
            self.logger.error(f"An error occurred fetching emails: {error}")

    def process_single_email(self, msg_id, thread_id):
        try:
            # Fetch full message details
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            
            payload = message['payload']
            headers = payload.get('headers', [])
            
            # Extract headers
            subject = ""
            sender = ""
            reply_to = ""
            date_str = ""
            
            for h in headers:
                name = h['name'].lower()
                if name == 'subject':
                    subject = h['value']
                elif name == 'from':
                    sender = h['value']
                elif name == 'reply-to':
                    reply_to = h['value']
                elif name == 'date':
                    date_str = h['value']

            # Extract Body
            body = self._get_email_body(payload)
            
            # Use msg_id as unique ID
            email_id_str = f"gmail_{msg_id}"
            
            email_data_headers = {
                "From": sender,
                "Reply-To": reply_to,
                "Subject": subject,
                "Date": date_str
            }
            
            self.logger.info(f"Ingesting: {subject} from {sender}")
            
            # Push to Queue
            try:
                push_email_to_queue(email_id_str, email_data_headers, body)
                # self.logger.info(f"Pushed {email_id_str} to DB.")
                
                # OPTIONAL: Mark as read?
                # User didn't strictly ask to mark as read, but usually agents do.
                # Currently leaving as UNSEEN so user can verify.
                # If we want to mark read:
                # self.service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNSEEN']}).execute()
                
            except Exception as db_err:
                self.logger.error(f"DB Push Failed: {db_err}")

        except Exception as e:
            self.logger.error(f"Failed to process message {msg_id}: {e}")

    def _get_email_body(self, payload):
        """
        Recursively extracts body from Gmail API payload.
        Prioritizes text/plain, then text/html.
        Strictly ignores attachments.
        """
        body = ""
        
        parts = payload.get('parts')
        
        # If no parts, body might be in 'body.data' of the payload itself
        if not parts:
            data = payload.get('body', {}).get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode(errors='ignore')
            return ""

        # Recursive search implementation or iterative?
        # Let's simple DFS for text/plain
        
        def find_part(parts_list, mime_type):
            for part in parts_list:
                # Ignore attachments
                if part.get('filename') and part.get('filename') != "": 
                    continue
                
                if part.get('mimeType') == mime_type:
                    data = part.get('body', {}).get('data')
                    if data:
                        return base64.urlsafe_b64decode(data).decode(errors='ignore')
                
                if part.get('parts'):
                    found = find_part(part['parts'], mime_type)
                    if found: return found
            return None

        # Try plain first
        body = find_part(parts, 'text/plain')
        if not body:
            # Try HTML
            body = find_part(parts, 'text/html')
            
        return body or "(No readable text body found)"
