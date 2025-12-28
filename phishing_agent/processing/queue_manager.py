import json
import os
import time
import logging
from datetime import datetime

QUEUE_FILE = "database/queue.json"
logger = logging.getLogger("QueueManager")

def init_db():
    """Initializes the JSON queue file if it doesn't exist."""
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    if not os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'w') as f:
            json.dump([], f, indent=4)
        logger.info(f"Initialized new queue file at {QUEUE_FILE}")

def _read_queue():
    try:
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def _write_queue(data):
    with open(QUEUE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def push_email_to_queue(email_id, headers, body):
    """
    Pushes an email to the JSON queue if it doesn't already exist.
    """
    queue = _read_queue()
    
    # Check for duplicates
    for item in queue:
        if item.get('id') == email_id:
            logger.debug(f"[Queue] Email {email_id} already exists. Skipping.")
            return

    # Add new item
    # Note: validation assumes headers is a dict not a string, but the previous code passed json.dumps(headers).
    # We should clean this up. Main.py/Ingestion passes real dicts now?
    # Actually ingestion passes a dict to headers argument.
    # We will store it as a dict in JSON for readability.
    
    new_item = {
        "id": email_id,
        "headers": headers,
        "body": body if body else "(No Body Content)",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": None,
        "analysis_report": None
    }

    queue.append(new_item)
    _write_queue(queue)
    logger.info(f"[Queue] Email {email_id} added to JSON.")

def fetch_next_job():
    """
    Returns the first email with status='pending'.
    Returns a dict with 'id', 'headers', 'body'.
    """
    queue = _read_queue()
    for item in queue:
        if item.get('status') == 'pending':
            return {
                "id": item['id'],
                "headers": item['headers'], # Ensure this matches what worker expects
                "body": item['body']
            }
    return None

def update_job_status(job_id, status, analysis_result=None):
    """
    Updates the status and result of a job.
    """
    queue = _read_queue()
    updated = False
    for item in queue:
        if item.get('id') == job_id:
            item['status'] = status
            item['updated_at'] = datetime.now().isoformat()
            if analysis_result:
                item['analysis_report'] = analysis_result
                # Also set risk_score if available
                if 'score' in analysis_result:
                    item['risk_score'] = analysis_result['score']
            
            # PRIVACY: Scrub raw content once processing is complete
            if status == "completed":
                item['body'] = None
                item['headers'] = None

            updated = True
            break
    
    if updated:
        _write_queue(queue)
    else:
        logger.warning(f"[Queue] Could not find job {job_id} to update.")

def fetch_all_results():
    """
    Returns all items that have a completed analysis_report, sorted by created_at desc.
    Returns list of analysis_report dicts (legacy format support)
    """
    queue = _read_queue()
    results = []
    
    # Sort by created_at descending (newest first)
    # created_at is ISO string
    queue.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    for item in queue:
        if item.get('status') == 'completed' and item.get('analysis_report'):
             report = item['analysis_report']
             # Ensure ID is present in the report object for the dashboard
             if 'id' not in report:
                 report['id'] = item['id']
             results.append(report)
             
    return results

def clear_db():
    """Clears the queue database and resets it to an empty list."""
    _write_queue([])
    logger.info("Database cleared.")