# main.py
import threading
import queue
import time
import signal
import sys
import json
from config import setup_logging
from agents.orchestrator import Orchestrator

# Import Dashboard Modules
from dashboard.renderer import render_dashboard
from dashboard.server import serve_dashboard

# Import Production Modules
from processing.queue_manager import init_db, fetch_next_job, update_job_status, fetch_all_results
from processing.ingestion import GmailIngestor
from analysis.structural import extract_urls

# Initialize Logging
logger = setup_logging()
analyzer = Orchestrator(logger)
running = True

def _parse_auth_header(auth_str):
    """Simple parser to convert Auth-Results string to dict for the analysis module"""
    res = {}
    if not auth_str: return res
    auth_str = auth_str.lower()
    if "spf=pass" in auth_str: res['spf'] = "pass"
    elif "spf=fail" in auth_str: res['spf'] = "fail"
    
    if "dkim=pass" in auth_str: res['dkim'] = "pass"
    elif "dkim=fail" in auth_str: res['dkim'] = "fail"
    
    if "dmarc=pass" in auth_str: res['dmarc'] = "pass"
    elif "dmarc=fail" in auth_str: res['dmarc'] = "fail"
    return res

def worker():
    logger.info("Worker thread started. Polling JSON Queue for jobs...")
    while running:
        try:
            # 1. Fetch next pending job (returns dictionary or None)
            job = fetch_next_job() 
            
            if not job:
                time.sleep(2)
                continue
                
            email_id = job['id']
            headers = job['headers']
            body = job['body']

            logger.info(f"Worker picked up {email_id}...")
            
            # headers is already a dict in our new JSON structure
            
            email_data = {
                "id": email_id,
                "headers": headers,
                "from": headers.get("From", "Unknown"),
                "subject": headers.get("Subject", "No Subject"),
                "reply_to": headers.get("Reply-To"),
                "body": body if body else "",
                "urls": extract_urls(body) if body else [],
                "auth_headers": _parse_auth_header(headers.get("Authentication-Results", ""))
            }
            
            # 2. Analyze
            update_job_status(email_id, "processing")
            result = analyzer.process_email(email_data)
            
            # Enhance result with display metadata
            result['sender'] = email_data['from']
            result['subject'] = email_data['subject']
            
            # 3. Save Result
            update_job_status(email_id, "completed", result)
            logger.info(f"Analysis Complete {email_id} => Score: {result['score']}")
            
        except Exception as e:
            logger.error(f"Worker Error: {e}", exc_info=True)
            time.sleep(2)

def ingestion_service():
    """Runs the real Gmail API ingestion every 30 seconds"""
    ingestor = GmailIngestor()
    try:
        if not ingestor.authenticate():
            logger.critical("Ingestion authentication failed. Exiting ingestion thread.")
            return

        while running:
            logger.info("Ingestion: Checking for new emails...")
            ingestor.fetch_emails(lookback_limit=10)
            time.sleep(30) # Poll interval
    except Exception as e:
        logger.error(f"Ingestion Error: {e}")

def main():
    global running
    logger.info("System Initializing (v1 Production - JSON Mode)...")
    
    # 1. Initialize DB (JSON File)
    init_db()

    # 2. Start Analysis Worker
    worker_thread = threading.Thread(target=worker, name="Worker-1", daemon=True)
    worker_thread.start()

    # 3. Start Ingestion Service
    ingestor_thread = threading.Thread(target=ingestion_service, name="Ingestion", daemon=True)
    ingestor_thread.start()

    # 4. Dashboard Server (Main Thread)
    try:
        logger.info("Starting Dashboard Server...")
        logger.info("Dashboard auto-refresh enabled.")
        
        server_thread = threading.Thread(target=serve_dashboard, daemon=True)
        server_thread.start()
        
        while running:
            # Refresh Dashboard HTML every 10 seconds
            try:
                results = fetch_all_results() # Now returns list of dicts
                render_dashboard(results)
            except Exception as e:
                logger.error(f"Dashboard Update Error: {e}")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        logger.info("Stopping...")
        running = False
        
    worker_thread.join(timeout=2)
    ingestor_thread.join(timeout=2)
    logger.info("System Shutdown.")

if __name__ == "__main__":
    main()