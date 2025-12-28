from .technical_agent import TechnicalAgent
from .semantic_agent import SemanticAgent
import logging

class Orchestrator:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("Orchestrator")
        self.technical_agent = TechnicalAgent(self.logger)
        self.semantic_agent = SemanticAgent(self.logger)

    def process_email(self, email_data):
        self.logger.info(f"Orchestrator: Starting analysis for {email_data.get('id', 'Unknown')}")
        
        final_reasons = []
        final_score = 0

        # 1. Technical Analysis
        tech_result = self.technical_agent.analyze(email_data)
        final_reasons.extend(tech_result['reasons'])
        tech_score = tech_result['risk_score']
        
        final_score = max(final_score, tech_score)

        # 2. Optimization: Skip Semantic if Technical score is very high (verified malicious)
        if tech_score >= 80:
            self.logger.info("Orchestrator: High technical risk detected. Skipping semantic analysis.")
        else:
            # 3. Semantic Analysis
            sem_result = self.semantic_agent.analyze(email_data)
            final_reasons.extend(sem_result['reasons'])
            sem_score = sem_result['risk_score']
            final_score = max(final_score, sem_score)

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
