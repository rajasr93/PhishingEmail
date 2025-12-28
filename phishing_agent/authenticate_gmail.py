import os
import config
from google_auth_oauthlib.flow import InstalledAppFlow

# Define scopes (must match ingestion.py)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

def force_auth():
    print("--- STARTING MANUAL AUTH ---")
    
    if not os.path.exists(config.CREDENTIALS_FILE):
        print(f"ERROR: {config.CREDENTIALS_FILE} not found.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        config.CREDENTIALS_FILE, SCOPES)
    
    # Run slightly differently to force printing URL if browser fails
    # using basic console strategy implies no local server usually, 
    # but we want the redirect to localhost:8080 to work.
    
    print(f"Please look for a URL below or in a browser window.")
    
    # We use run_local_server but we wrap it to ensure we catch output? 
    # Actually, flow.run_local_server() usually prints "Please visit this URL" to stdout 
    # if it can't open the browser. 
    # But to be safe, let's redirect stdout to file in the wrapper command or 
    # use run_console() if we want copy-paste (but user set localhost redirect).
    
    try:
        # Manually generate and print URL
        auth_url, _ = flow.authorization_url(prompt='consent')
        print(f"\n\n--- CLICK THIS URL TO LOGIN ---\n{auth_url}\n-------------------------------\n")
        
        # Start server to catch the callback
        creds = flow.run_local_server(port=8080, open_browser=False)
        
        # Save token
        with open(config.TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
        print("SUCCESS: token.json created.")
        
    except Exception as e:
        print(f"AUTH FAILED: {e}")

if __name__ == "__main__":
    force_auth()
