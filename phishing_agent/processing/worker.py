import time
import json
import logging
from processing.queue_manager import fetch_next_job, mark_job_complete, update_status
from analysis.pipeline import analyze_email_content

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Worker] - %(message)s')
logger = logging.getLogger(__name__)

def run_worker():
    """
    v1 Runtime Loop: Serialized execution.
    Fetches one email at a time from the persistent queue.
    """
    logger.info("Service started. Waiting for jobs...")
    
    while True:
        # 1. Fetch next PENDING job (Consumer)
        job = fetch_next_job()
        
        if not job:
            time.sleep(1) # Prevent CPU spin
            continue

        email_id, raw_headers, raw_body = job
        
        try:
            logger.info(f"Processing {email_id}...")
            
            # 2. Deserialize Data
            headers = json.loads(raw_headers) if raw_headers else {}
            
            email_data = {
                "id": email_id,
                "headers": headers,
                "body": raw_body
            }

            # 3. Execute Analysis Pipeline
            report = analyze_email_content(email_data)
            
            # 4. Save Results
            mark_job_complete(email_id, report['score'], report)
            logger.info(f"Finished {email_id}. Risk: {report['score']} ({report['primary_reason']})")
            
        except Exception as e:
            logger.error(f"Failed to process {email_id}: {e}")
            update_status(email_id, "FAILED")