from agents.orchestrator import Orchestrator
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def test_orchestrator():
    print("Initializing Orchestrator...")
    orchestrator = Orchestrator()
    
    mock_email = {
        "id": "test_001",
        "headers": {
            "From": "suspicious@example.com",
            "Subject": "Urgent Invoice"
        },
        "body": "Please pay this invoice immediately at http://malicious-site.com/login"
    }

    print("Running process_email...")
    result = orchestrator.process_email(mock_email)
    print("Result:", result)
    
    if result['score'] >= 0:
        print("SUCCESS: Orchestrator returned a valid result.")
    else:
        print("FAILURE: Invalid result.")

if __name__ == "__main__":
    test_orchestrator()
