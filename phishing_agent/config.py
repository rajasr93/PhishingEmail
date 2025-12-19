import os

# --- Runtime Constraints (v1) ---
# Enforces serialized execution to prevent CPU exhaustion
#MAX_WORKERS = 1                 
#DB_PATH = os.path.join("database", "queue_db.sqlite")

# --- Analysis Timeouts (Seconds) ---
# Hard timeouts to prevent hangs during network analysis
#DNS_TIMEOUT = 3.0
#HTTP_TIMEOUT = 5.0

# --- Risk Thresholds ---
#HIGH_RISK_THRESHOLD = 80
#MEDIUM_RISK_THRESHOLD = 50

# --- Feature Flags ---
#ENABLE_HEADLESS_BROWSER = False
# config.py
import logging
import sys

# v1 Requirement: Hard timeouts for analysis steps [cite: 102]
TIMEOUT_DNS = 2  # seconds
TIMEOUT_ML = 1   # seconds

def setup_logging():
    """
    Configures logging to show timestamps, thread names, and log levels.
    This helps identify if the Worker thread is actually running.
    """
    logging.basicConfig(
        level=logging.INFO, # Change to DEBUG for even more detail
        format="%(asctime)s - [%(levelname)s] - [%(threadName)s] - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout) # Ensure output goes to console immediately
        ]
    )
    return logging.getLogger("PhishingAgent")