# config.py
import os

# Version 1 Constraints
MAX_CONCURRENT_WORKERS = 1  # Serialized execution 
network_timeout_seconds = 5  # Hard timeout for DNS/WHOIS [cite: 29]

# Paths
DB_PATH = os.path.join("database", "queue_db.sqlite")
MODEL_PATH = os.path.join("models", "phishing_intent_v1.onnx")

# Feature Flags
ENABLE_HEADLESS_BROWSER = False # Disabled for v1/v2, enabled in v3 [cite: 45]