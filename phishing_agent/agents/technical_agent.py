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
        headers = email_data.get('headers')
        if headers is None: headers = {}
        reply_to_score, reply_to_reasons = self._check_reply_to(headers)
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

        applied_penalties = set()

        for url in urls:
            # Wrap blocking network call in executor
            sandbox_res = await loop.run_in_executor(None, check_dns_redirects, url)
            
            if sandbox_res:
                # Phase 2: Source-Destination Consistency Check
                is_safe_redirect = False
                reason_key = sandbox_res.get('reason')

                if "Excessive Redirects" in reason_key:
                    final_url = sandbox_res.get('final_url')
                    sender_email = email_data.get('headers', {}).get('From', '')
                    
                    if final_url and sender_email:
                        sender_domain = self._get_domain_from_email(sender_email)
                        final_domain = self._get_domain_from_url(final_url)
                        
                        if sender_domain and final_domain:
                            if final_domain == sender_domain or final_domain.endswith("." + sender_domain):
                                is_safe_redirect = True
                                self.logger.info(f"Consistency Check Passed: {sender_domain} -> {final_domain}")

                if not is_safe_redirect:
                    # Phase 3: Penalty Deduplication
                    # Only apply penalty once per risk type (reason)
                    if reason_key not in applied_penalties:
                        risk_score += sandbox_res.get('severity', 0)
                        applied_penalties.add(reason_key)
                    
                    # Always append reason for visibility, but maybe dedupe text too?
                    # User asked for deduplication of PENALTY (score).
                    # But usually dashboard clutter is bad too.
                    # "URL: Unresolvable Domain (...)".
                    # If I have 10, maybe I should list them all but score once?
                    # Or verify dashboard? Dashboard lists All reasons.
                    # The prompt said "Deduplicate Penalties: ... max 1 penalty per type"
                    # It implied score cap.
                    # But "if an email has 10 links ... 10x penalty"
                    # I will dedupe reasons too to keep UI clean.
                    if reason_key in applied_penalties and len([r for r in reasons if reason_key in r]) > 0:
                        continue # Skip adding duplicate reason text
                    
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

    def _get_domain_from_email(self, email_str):
        """Extracts domain from 'Name <email@domain.com>'"""
        import re
        match = re.search(r"@([\w.-]+)", email_str)
        if match:
            return match.group(1).lower()
        return ""

    def _get_domain_from_url(self, url):
        import urllib.parse
        try:
            return urllib.parse.urlparse(url).netloc.lower()
        except:
            return ""
