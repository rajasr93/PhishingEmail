# main.py
import threading
import queue
import time
from config import setup_logging
from core_logic import PhishingAnalyzer

# Import Dashboard Modules
from dashboard.renderer import render_dashboard
from dashboard.server import serve_dashboard  # <--- IMPORT NEW SERVER

# Initialize Logging
logger = setup_logging()

# v1 Runtime: In-memory queue
job_queue = queue.Queue()
analysis_results = []
analyzer = PhishingAnalyzer(logger)

def worker():
    logger.info("Worker thread started. Waiting for jobs...")
    while True:
        try:
            email_data = job_queue.get(block=True, timeout=5)
        except queue.Empty:
            continue

        if email_data is None:
            break

        try:
            logger.info(f"Worker picked up {email_data['id']}...")
            result = analyzer.analyze_email(email_data)
            analysis_results.append(result)
            logger.info(f"DASHBOARD ALERT >>> {result}")
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            job_queue.task_done()

def ingestion_simulator():
    sample_emails = [
        {
            "id": "email_001",
            "from": "ceo@company.com",
            "reply_to": "ceo@gmail.com",
            "body": "Please wire funds immediately.",
            "urls": ["http://company-secure-login.com"],
            "auth_headers": {"spf": "pass", "dkim": "pass"}
        },
        {
            "id": "email_002",
            "from": "newsletter@marketing.com",
            "reply_to": "newsletter@marketing.com",
            "body": "Check out our weekly deals.",
            "urls": ["http://short.ly/xyz"],
            "auth_headers": {"spf": "pass"}
        },
        {
            "id": "email_003_spoof",
            "from": "support@bank.com",
            "reply_to": "support@bank.com",
            "body": "Your account is compromised. Take immediate action.",
            "urls": ["http://bank-verify.com"],
            "auth_headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"}
        }
    ]

    logger.info("Ingestion service started.")
    for email in sample_emails:
        time.sleep(1)
        logger.info(f"Ingestion: Receiving {email['id']}...")
        job_queue.put(email)
    
    logger.info("Ingestion complete.")

def main():
    logger.info("System Initializing (v1 Runtime)...")

    # Start Worker
    worker_thread = threading.Thread(target=worker, name="Worker-1", daemon=True)
    worker_thread.start()

    # Run Ingestion
    ingestion_simulator()

    # Wait for queue to empty
    job_queue.join()
    
    # 1. Generate the HTML File
    logger.info("Generating Dashboard...")
    render_dashboard(analysis_results)
    
    # 2. Serve the Dashboard (Blocks until Ctrl+C)
    serve_dashboard()
    
    # 3. Clean up
    logger.info("System shutting down.")
    
    # 4. Stop the worker thread
    job_queue.put(None)
    worker_thread.join()
    

if __name__ == "__main__":
    main()