# core_logic.py
import time
from config import TIMEOUT_DNS
from auth_validator import AuthValidator # Import the new module

class PhishingAnalyzer:
    def __init__(self, logger):
        self.logger = logger
        self.auth_checker = AuthValidator() # Initialize validator

    def analyze_email(self, email_data):
        email_id = email_data.get('id')
        self.logger.info(f"Starting analysis for {email_id}...")

        risk_score = 0
        reasons = []
        
        # --- Step 1: Header Parsing ---
        self.logger.info(f"[{email_id}] Step 1: Parsing Headers...")
        if email_data.get('reply_to') != email_data.get('from'):
            risk_score += 30
            reasons.append("Reply-To mismatch detected")

        # --- Step 2: URL & Artifact Extraction ---
        self.logger.info(f"[{email_id}] Step 2: Extracting URLs...")
        urls = email_data.get('urls', [])
        
        # --- Step 3: Sandbox Analysis ---
        self.logger.info(f"[{email_id}] Step 3: Sandboxing {len(urls)} URLs...")
        time.sleep(0.5) 
        for url in urls:
            if "short.ly" in url:
                risk_score += 20
                reasons.append(f"URL Shortener detected: {url}")

        # --- NEW STEP: Email Authentication ---
        self.logger.info(f"[{email_id}] Step 3b: Checking Auth Protocols (SPF/DKIM)...")
        auth_score, auth_reasons = self.auth_checker.validate(email_data)
        risk_score += auth_score
        reasons.extend(auth_reasons)

        # --- Step 4: ML Intent Analysis ---
        self.logger.info(f"[{email_id}] Step 4: ML Intent Analysis...")
        if "immediate action" in email_data.get('body', '').lower():
            risk_score += 40
            reasons.append("High urgency language detected")

        # --- Step 5: Risk Aggregation (Worst-Link Elevation) ---
        self.logger.info(f"[{email_id}] Step 5: Aggregating Risk...")
        
        # Heuristic: If Auth fails AND Urgency is high, force PHISHING verdict
        if auth_score > 0 and "High urgency language detected" in reasons:
            risk_score = max(risk_score, 85) # Elevate risk
            reasons.append("CRITICAL: Auth failure combined with urgency")

        final_verdict = "SAFE"
        if risk_score >= 50:
            final_verdict = "PHISHING"
        elif risk_score >= 30:
            final_verdict = "SUSPICIOUS" # Added granularity
        
        result = {
            "id": email_id,
            "sender": email_data.get('from', 'Unknown'), # Add Sender
            "verdict": final_verdict,
            "verdict": final_verdict,
            "score": risk_score,
            "reasons": reasons,
            "subject": email_data.get('subject', 'No Subject')
        }
        
        return result