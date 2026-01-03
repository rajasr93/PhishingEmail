
import os
import sys
import logging
import importlib

# Configure logging to console
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("SetupCheck")

def check_file(path, description):
    if os.path.exists(path):
        logger.info(f"✅ {description} found: {path}")
        return True
    else:
        logger.error(f"❌ {description} NOT found at: {path}")
        return False

def check_dependency(package_name):
    try:
        importlib.import_module(package_name)
        logger.info(f"✅ Dependency '{package_name}' installed.")
        return True
    except ImportError:
        logger.error(f"❌ Dependency '{package_name}' is MISSING. Run: pip install -r requirements.txt")
        return False

def main():
    logger.info("========================================")
    logger.info("🛡️  PhishingAgent Environment Check 🛡️")
    logger.info("========================================")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    all_good = True

    # 1. Check Python Dependencies
    logger.info("\n--- 1. Checking Dependencies ---")
    essential_pkgs = [
        "google.auth", 
        "googleapiclient", 
        "transformers", 
        "torch", 
        "requests"
    ]
    for pkg in essential_pkgs:
        if not check_dependency(pkg):
            all_good = False

    # 2. Check Configuration Files
    logger.info("\n--- 2. Checking Configuration ---")
    creds_path = os.path.join(base_dir, "credentials.json")
    if not check_file(creds_path, "Google Credentials"):
        logger.warning("   -> Action: Download 'OAuth Client ID' JSON from Google Cloud and save it as 'credentials.json' in this folder.")
        all_good = False

    # 3. Check AI Model
    logger.info("\n--- 3. Checking AI Model ---")
    model_path = os.path.join(base_dir, "models", "bert_phishing")
    if os.path.exists(model_path):
        # Basic check if it's not empty
        if len(os.listdir(model_path)) > 0:
            logger.info(f"✅ AI Model found at: {model_path}")
        else:
            logger.error(f"❌ AI Model directory exists but is empty: {model_path}")
            all_good = False
    else:
        logger.error(f"❌ AI Model NOT found at: {model_path}")
        logger.warning("   -> Action: Run 'python3 phishing_agent/download_model.py' to cache the model locally.")
        all_good = False

    # 4. Check Database Directory
    logger.info("\n--- 4. Checking Data Store ---")
    db_dir = os.path.join(base_dir, "database")
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir)
            logger.info(f"✅ Created missing database folder: {db_dir}")
        except Exception as e:
            logger.error(f"❌ Could not create database folder: {e}")
            all_good = False
    else:
        logger.info(f"✅ Database folder exists.")

    logger.info("\n========================================")
    if all_good:
        logger.info("🚀 SYSTEM READY! You can safely run 'python3 phishing_agent/main.py'")
        sys.exit(0)
    else:
        logger.error("🛑 SETUP INCOMPLETE. Please fix the errors above before running the agent.")
        sys.exit(1)

if __name__ == "__main__":
    main()
