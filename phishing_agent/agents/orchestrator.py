from .technical_agent import TechnicalAgent
from .semantic_agent import SemanticAgent
import logging

class Orchestrator:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("Orchestrator")
        self.technical_agent = TechnicalAgent(self.logger)
        self.semantic_agent = SemanticAgent(self.logger)

    async def process_email(self, email_data):
        self.logger.info(f"Orchestrator: Starting analysis for {email_data.get('id', 'Unknown')}")
        
        final_reasons = []
        final_score = 0
        
        import asyncio

        # Run agents in parallel
        # Note: We are sacrificing the "short-circuit" optimization for speed/parallelism as requested
        tech_task = self.technical_agent.analyze(email_data)
        sem_task = self.semantic_agent.analyze(email_data)

        results = await asyncio.gather(tech_task, sem_task, return_exceptions=True)
        tech_result = results[0]
        sem_result = results[1]

        # 1. Unpack Results
        if isinstance(tech_result, dict):
            tech_score = tech_result.get('risk_score', 0)
            tech_reasons_list = tech_result.get('reasons', [])
        else:
            self.logger.error(f"TechnicalAgent failed: {tech_result}")
            tech_score = 0
            tech_reasons_list = ["Error: Technical Analysis Failed"]

        if isinstance(sem_result, dict):
            sem_score = sem_result.get('risk_score', 0)
            sem_reasons_list = sem_result.get('reasons', [])
        else:
            self.logger.error(f"SemanticAgent failed: {sem_result}")
            sem_score = 0
            sem_reasons_list = ["Error: Semantic Analysis Failed"]

        # 2. Semantic Trust Override (REMOVED due to Security Audit)
        # Previously trusted sender if tech_score < 10, but this ignores compromised accounts.
        # Logic removed to respect High Phishing Probability from AI.

        
        # 3. Aggregate Final Reasons
        final_reasons.extend(tech_reasons_list)
        final_reasons.extend(sem_reasons_list)
        
        final_score = max(final_score, tech_score)
        
        # Additive Logic: Sum scores to reflect cumulative risk
        final_score = min(tech_score + sem_score, 100)

        # 3. Worst-Link Logic (Cross-Correlated Elevation)
        tech_reasons = tech_result.get('reasons', []) if isinstance(tech_result, dict) else []
        sem_reasons = sem_result.get('reasons', []) if isinstance(sem_result, dict) else []
        
        has_auth_fail = any("Validation Failed" in r or "Signature Invalid" in r or "Policy Violation" in r for r in tech_reasons)
        has_urgency = any("Urgency Detected" in r for r in sem_reasons)
        
        if has_auth_fail and has_urgency:
            if final_score < 85:
                final_score = 85
                final_reasons.insert(0, "CRITICAL: Auth Failure + High Urgency Detected")

        import config
        
        # 4. Determine Verdict
        verdict = "SAFE"
        if final_score >= config.HIGH_RISK_THRESHOLD:
            verdict = "PHISHING"
        elif final_score >= config.MEDIUM_RISK_THRESHOLD:
            verdict = "SUSPICIOUS"

        return {
            "score": final_score,
            "verdict": verdict,
            "primary_reason": final_reasons[0] if final_reasons else "Clean",
            "reasons": final_reasons
        }
