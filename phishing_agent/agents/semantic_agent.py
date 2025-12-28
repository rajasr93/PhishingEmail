from .base_agent import BaseAgent

import torch

class SemanticAgent(BaseAgent):
    def __init__(self, logger=None, use_ai=True):
        super().__init__("SemanticAgent", logger)
        self.use_ai = use_ai
        self.tokenizer = None
        self.model = None
        self.model_name = "ealvaradob/bert-finetuned-phishing"

    def _load_model(self):
        if self.tokenizer is None or self.model is None:
            self.logger.info("Loading BERT model for SemanticAgent...")
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import os
            
            # Check for local model first
            local_path = "./models/bert_phishing"
            if os.path.exists(local_path):
                 self.model_name = local_path
                 self.logger.info(f"Using local model at {local_path}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.logger.info("BERT model loaded.")

    async def analyze(self, email_data):
        self.logger.info("SemanticAgent execution started.")
        risk_score = 0
        reasons = []
        body = email_data.get('body', "")

        # 1. Fast Keyword Check
        intent_res = self._infer_intent(body)
        if intent_res:
            risk_score += intent_res.get('severity', 0)
            reasons.append(f"Keyword: {intent_res.get('reason')}")

        # 2. AI Model Check
        if self.use_ai and body:
            try:
                # Run model loading and inference in executor to avoid blocking event loop
                import asyncio
                loop = asyncio.get_running_loop()
                
                def _run_ai_inference():
                    self._load_model()
                    inputs = self.tokenizer(body, return_tensors="pt", truncation=True, max_length=512)
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                    
                    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
                    return probabilities[0][1].item()

                phishing_prob = await loop.run_in_executor(None, _run_ai_inference)
                
                if phishing_prob > 0.75:
                    ai_score = int(phishing_prob * 100)
                    risk_score = max(risk_score, ai_score) # Take the higher of keyword or AI
                    reasons.append(f"AI: High Phishing Probability ({ai_score}%)")
                    
            except Exception as e:
                self.logger.error(f"SemanticAgent AI Error: {e}")

        return {
            "risk_score": min(risk_score, 100),
            "reasons": reasons
        }

    def _infer_intent(self, text):
        """Heuristic check for Urgency and BEC patterns."""
        text = text.lower() if text else ""
        urgency_words = ['urgent', 'immediate', '24 hours', 'suspend']
        credential_words = ['password', 'login', 'verify account']
        
        if any(w in text for w in urgency_words):
            return {"severity": 40, "reason": "Urgency Detected", "detail": "High urgency keywords"}
        
        if any(w in text for w in credential_words):
            return {"severity": 40, "reason": "Credential Request", "detail": "Login keywords"}
            
        return None
