# processing/worker.py

# ... other imports ...
from analysis.pipeline import analyze_email_content  # <--- This import now works

def run_worker():
    # ... inside the loop ...
    # 1. Fetch Job
    # 2. Prepare Data
    email_data = {"headers": headers, "body": body}
    
    # 3. Run Pipeline
    result = analyze_email_content(email_data)
    
    # 4. Save Result
    # ...