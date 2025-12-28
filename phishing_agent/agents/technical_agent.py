from .base_agent import BaseAgent
from analysis.headers import analyze_headers
from analysis.structural import extract_urls
from analysis.sandbox import check_dns_redirects

class TechnicalAgent(BaseAgent):
    def __init__(self, logger=None):
        super().__init__("TechnicalAgent", logger)

    async def analyze(self, email_data):
        self.logger.info("TechnicalAgent execution started.")
        risk_score = 0
        reasons = []

        # 1. Header Analysis (CPU bound, fast enough to run synchronously or wrap if very complex)
        # analyze_headers is fast, keeping it sync for now
        header_res = analyze_headers(email_data.get('headers', {}))
        if header_res:
            risk_score += header_res.get('severity', 0)
            reasons.append(f"Header: {header_res.get('reason')}")

        # 2. URL Extraction & Analysis
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
