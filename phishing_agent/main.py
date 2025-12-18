import threading
import time
from core.queue_manager import init_db, push_email_to_queue
from worker import run_worker

# Mock Ingestion for testing v1 behavior
def mock_ingestion_loop():
    """Simulates incoming emails (Producer)"""
    test_emails = [
        ("email_001", {"From": "boss@company.com", "Reply-To": "hacker@evil.com"}, "Please reset your password urgent."),
        ("email_002", {"From": "service@amazon.com", "Reply-To": "service@amazon.com"}, "Your order has shipped."),
    ]
    
    for eid, headers, body in test_emails:
        time.sleep(1)
        push_email_to_queue(eid, headers, body)

if __name__ == "__main__":
    # 1. Initialize System
    init_db()
    
    # 2. Start Worker Thread (Consumer)
    # v1 uses a single worker thread 
    worker_thread = threading.Thread(target=run_worker, daemon=True)
    worker_thread.start()
    
    # 3. Start Ingestion (Producer)
    mock_ingestion_loop()
    
    # Keep main thread alive
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")