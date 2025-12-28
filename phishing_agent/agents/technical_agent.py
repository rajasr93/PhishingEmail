from .base_agent import BaseAgent

from analysis.structural import extract_urls
from analysis.sandbox import check_dns_redirects

class TechnicalAgent(BaseAgent):
    def __init__(self, logger=None):
        super().__init__("TechnicalAgent", logger)

    async def analyze(self, email_data):
        self.logger.info("TechnicalAgent execution started.")
        risk_score = 0
        reasons = []

        # 1. Header Analysis (Reply-To Mismatch)
        reply_to_score, reply_to_reasons = self._check_reply_to(email_data.get('headers', {}))
        if reply_to_score > 0:
            risk_score += reply_to_score
            reasons.extend(reply_to_reasons)

        # 2. Auth Validation (SPF/DKIM/DMARC)
        auth_headers = self._parse_auth_header(email_data.get('headers', {}).get('Authentication-Results', ''))
        auth_score, auth_reasons = self._check_auth(auth_headers)
        if auth_score > 0:
            risk_score += auth_score
            reasons.extend(auth_reasons)

        # 3. URL Extraction & Analysis
        body = email_data.get('body', "")
        urls = extract_urls(body)
        
        import asyncio
        loop = asyncio.get_running_loop()

        for url in urls:
            # Wrap blocking network call in executor
            sandbox_res = await loop.run_in_executor(None, check_dns_redirects, url)
            
            if sandbox_res:
                risk_score += sandbox_res.get('severity', 0)
                reasons.append(f"URL: {sandbox_res.get('reason')} ({sandbox_res.get('detail')})")

        # Cap score at 100
        risk_score = min(risk_score, 100)

        return {
            "risk_score": risk_score,
            "reasons": reasons
        }

    def _parse_auth_header(self, auth_str):
        """Robust parser to convert Auth-Results string to dict using Regex."""
        res = {}
        if not auth_str: return res
        auth_str = auth_str.lower()
        
        import re
        # Regex to capture key=value pairs (e.g., spf=pass, dkim=fail)
        # Handles optional spaces around equals sign
        patterns = {
            'spf': r"spf\s*=\s*([a-z]+)",
            'dkim': r"dkim\s*=\s*([a-z]+)",
            'dmarc': r"dmarc\s*=\s*([a-z]+)"
        }
        
        for key, pat in patterns.items():
            match = re.search(pat, auth_str)
            if match:
                res[key] = match.group(1)
        
        return res

    def _check_auth(self, auth_headers):
        """
        Validates SPF, DKIM, DMARC statuses.
        Returns (score, list_of_reasons).
        """
        score = 0
        reasons = []

        # 1. SPF Check
        spf_status = auth_headers.get("spf", "pass") 
        if spf_status != "pass":
            score += 25
            reasons.append(f"SPF Validation Failed: {spf_status}")
            self.logger.warning(f"SPF Check Failed")

        # 2. DKIM Check
        dkim_status = auth_headers.get("dkim", "pass")
        if dkim_status != "pass":
            score += 20
            reasons.append(f"DKIM Signature Invalid: {dkim_status}")

        # 3. DMARC Check
        dmarc_status = auth_headers.get("dmarc", "pass")
        if dmarc_status in ["fail", "quarantine"]:
            score += 40 
            reasons.append(f"DMARC Policy Violation: {dmarc_status}")

        return score, reasons

    def _check_reply_to(self, headers_dict):
        """Checks for Reply-To mismatches."""
        score = 0
        reasons = []
        
        from_addr = headers_dict.get('From', '')
        reply_to = headers_dict.get('Reply-To', '')
        
        if reply_to and from_addr:
            # Simple domain extraction
            def get_domain(email):
                try: return email.split('@')[-1].strip().lower().replace('>', '')
                except: return ""

            if get_domain(from_addr) != get_domain(reply_to):
                score += 30 # Matching the dashboard rule (+30 pts)
                reasons.append(f"Reply-To Mismatch (From: {from_addr})")
                
        return score, reasons
