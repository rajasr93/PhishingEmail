# auth_validator.py
import logging

class AuthValidator:
    def __init__(self):
        self.logger = logging.getLogger("PhishingAgent")

    def validate(self, email_data):
        """
        Parses Authentication-Results headers or simulates DNS checks.
        Returns a risk score and list of failure reasons.
        """
        score = 0
        reasons = []
        auth_headers = email_data.get("auth_headers", {})

        # 1. SPF Check (Sender Policy Framework)
        # Checks if the IP is authorized to send for the domain
        spf_status = auth_headers.get("spf", "pass") # Default to pass for safety in demo
        if spf_status != "pass":
            score += 25
            reasons.append(f"SPF Validation Failed: {spf_status}")
            self.logger.warning(f"[{email_data['id']}] SPF Check Failed")

        # 2. DKIM Check (DomainKeys Identified Mail)
        # Checks cryptographic signature integrity
        dkim_status = auth_headers.get("dkim", "pass")
        if dkim_status != "pass":
            score += 20
            reasons.append(f"DKIM Signature Invalid: {dkim_status}")

        # 3. DMARC Check (Domain-based Message Authentication)
        # Policy enforcement (Reject/Quarantine)
        dmarc_status = auth_headers.get("dmarc", "pass")
        if dmarc_status == "fail" or dmarc_status == "quarantine":
            # DMARC failure is a high-confidence signal
            score += 40 
            reasons.append(f"DMARC Policy Violation: {dmarc_status}")

        return score, reasons