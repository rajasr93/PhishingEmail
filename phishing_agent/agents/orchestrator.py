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

        results = await asyncio.gather(tech_task, sem_task)
        tech_result = results[0]
        sem_result = results[1]

        # 1. Process Technical Results
        final_reasons.extend(tech_result['reasons'])
        tech_score = tech_result['risk_score']
        final_score = max(final_score, tech_score)

        # 2. Process Semantic Results
        final_reasons.extend(sem_result['reasons'])
        sem_score = sem_result['risk_score']
        
        # Additive Logic: Sum scores to reflect cumulative risk
        final_score = min(tech_score + sem_score, 100)

        # 3. Worst-Link Logic (Cross-Correlated Elevation)
        has_auth_fail = any("Validation Failed" in r or "Signature Invalid" in r or "Policy Violation" in r for r in tech_result['reasons'])
        has_urgency = any("Urgency Detected" in r for r in sem_result['reasons'])
        
        if has_auth_fail and has_urgency:
            if final_score < 85:
                final_score = 85
                final_reasons.insert(0, "CRITICAL: Auth Failure + High Urgency Detected")

        # 4. Determine Verdict
        verdict = "SAFE"
        if final_score >= 70:
            verdict = "PHISHING"
        elif final_score >= 40:
            verdict = "SUSPICIOUS"

        return {
            "score": final_score,
            "verdict": verdict,
            "primary_reason": final_reasons[0] if final_reasons else "Clean",
            "reasons": final_reasons
        }
