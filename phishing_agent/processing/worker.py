import json
from processing.queue_manager import fetch_next_job, update_job_status
from agents.orchestrator import Orchestrator
from analysis.structural import extract_urls
import asyncio

def run_worker(logger, shutdown_event):
    """
    v2 Runtime Loop: Async execution with graceful shutdown.
    """
    
    async def async_worker_loop():
        logger.info("Service started. Waiting for jobs...")
        
        # Initialize the Orchestrator
        orchestrator = Orchestrator(logger)
        
        while not shutdown_event.is_set():
            # 1. Fetch next PENDING job (Consumer)
            # This is sync I/O, technically blocking but fast
            job = fetch_next_job()
            
            if not job:
                await asyncio.sleep(2) 
                continue
    
            email_id = job['id']
            headers = job['headers']
            body = job['body']
            
            try:
                logger.info(f"Processing {email_id}...")
                
                # 2. Deserialize Data if needed
                if isinstance(headers, str):
                    try:
                        headers = json.loads(headers)
                    except json.JSONDecodeError:
                        headers = {}

                email_data = {
                    "id": email_id,
                    "headers": headers,
                    "body": body,
                    "urls": extract_urls(body) if body else []
                    # Auth headers handling is now inside TechnicalAgent via headers
                }
    
                # 3. Execute Analysis Pipeline
                update_job_status(email_id, "processing")
                report = await orchestrator.process_email(email_data)
                
                # 4. Save Results
                # Enhance report with metadata for dashboard
                report['sender'] = headers.get("From", "Unknown") if isinstance(headers, dict) else "Unknown"
                report['subject'] = headers.get("Subject", "No Subject") if isinstance(headers, dict) else "No Subject"

                update_job_status(email_id, "completed", report)
                logger.info(f"Finished {email_id}. Risk: {report['score']} ({report['primary_reason']})")
                
            except Exception as e:
                logger.error(f"Failed to process {email_id}: {e}", exc_info=True)
                update_job_status(email_id, "FAILED")
                
        logger.info("Worker loop stopping...")

    asyncio.run(async_worker_loop())