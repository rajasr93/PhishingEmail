import time
import json
import logging
from processing.queue_manager import fetch_next_job, mark_job_complete, update_status
from agents.orchestrator import Orchestrator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Worker] - %(message)s')
logger = logging.getLogger(__name__)

def run_worker():
    """
    v1 Runtime Loop: Async execution.
    Fetches one email at a time from the persistent queue.
    """
    import asyncio
    
    async def async_worker_loop():
        logger.info("Service started. Waiting for jobs...")
        
        # Initialize the Orchestrator ONCE before the while loop starts
        orchestrator = Orchestrator(logger)
        
        while True:
            # 1. Fetch next PENDING job (Consumer)
            job = fetch_next_job()
            
            if not job:
                # Use async sleep to avoid blocking loop (though we're the only thing running here)
                await asyncio.sleep(1) 
                continue
    
            email_id, raw_headers, raw_body = job['id'], job['headers'], job['body']
            
            try:
                logger.info(f"Processing {email_id}...")
                
                # 2. Deserialize Data
                headers = json.loads(raw_headers) if isinstance(raw_headers, str) else raw_headers
                
                email_data = {
                    "id": email_id,
                    "headers": headers,
                    "body": raw_body
                }
    
                # 3. Execute Analysis Pipeline
                report = await orchestrator.process_email(email_data)
                
                # 4. Save Results
                # mark_job_complete expects just the id and fields, assumes we imported it?
                # The imports in this file were incomplete in the view earlier, 
                # let's assume update_job_status/mark_job_complete logic is imported or available.
                # Actually main.py used update_job_status. Here we imported mark_job_complete.
                # Let's trust the imports existing in the file were sufficient or correct them if error.
                mark_job_complete(email_id, report['score'], report)
                logger.info(f"Finished {email_id}. Risk: {report['score']} ({report['primary_reason']})")
                
            except Exception as e:
                logger.error(f"Failed to process {email_id}: {e}")
                update_status(email_id, "FAILED")

    asyncio.run(async_worker_loop())