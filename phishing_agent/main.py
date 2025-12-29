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



from processing.worker import run_worker

def worker_thread_wrapper():
    """Wrapper to run the async worker in a thread with the global shutdown event"""
    # Create an event-like object or use a threading.Event if we want true signaling
    # For now, we reuse the 'running' global via a lambda or simple wrapper?
    # Actually, we need to pass a threading.Event. 
    # Let's change 'running' to an Event in main() or just wrap it here.
    
    # Adapt simple bool 'running' to Event for compatibility
    class CryptoShutdownEvent:
        def is_set(self):
            return not running
            
    run_worker(logger, CryptoShutdownEvent())

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
    
    # 0. Pre-Flight Check
    if not os.path.exists(CREDENTIALS_FILE):
        print_setup_banner()
        logger.error(f"Missing {CREDENTIALS_FILE}. Exiting.")
        return

    logger.info("System Initializing (v1 Production - JSON Mode)...")
    
    # 1. Initialize DB (JSON File)
    init_db()
    from processing.queue_manager import reset_stuck_jobs
    reset_stuck_jobs()

    # 2. Start Analysis Worker
    worker_thread = threading.Thread(target=worker_thread_wrapper, name="Worker-1", daemon=True)
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