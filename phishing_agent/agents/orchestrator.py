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

        # 1. Process Technical Results
        if isinstance(tech_result, dict):
            final_reasons.extend(tech_result.get('reasons', []))
            tech_score = tech_result.get('risk_score', 0)
            final_score = max(final_score, tech_score)
        else:
            self.logger.error(f"TechnicalAgent failed: {tech_result}")
            final_reasons.append("Error: Technical Analysis Failed")
            tech_score = 0

        # 2. Process Semantic Results
        if isinstance(sem_result, dict):
            final_reasons.extend(sem_result.get('reasons', []))
            sem_score = sem_result.get('risk_score', 0)
        else:
            self.logger.error(f"SemanticAgent failed: {sem_result}")
            final_reasons.append("Error: Semantic Analysis Failed")
            sem_score = 0
        
        # 2. Semantic Trust Override (False Positive Reduction)
        # If Technical Analysis is CLEAN (Score < 10) AND Auth passed (implied by low score),
        # we Trust the Sender and suppress wild AI hallucinations (e.g., "Order Confirmation" = Phishing).
        if tech_score < 10:
             if sem_score > 50:
                 # Downgrade AI score significantly but keep it visible as a 'Warning'
                 # or completely zero it out.
                 # Let's Cap it at 0 to ensure verdict is SAFE.
                 # Log only if we are overriding a high score
                 reasons = sem_result.get('reasons', [])
                 reasons.append(f"(AI Risk {sem_score}% Suppressed by Trusted Sender)")
                 sem_result['reasons'] = reasons # Update reasons
                 sem_score = 0
        
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
