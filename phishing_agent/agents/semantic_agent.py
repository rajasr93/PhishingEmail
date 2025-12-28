from .base_agent import BaseAgent
from analysis.ml_reasoning import infer_intent
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

    def analyze(self, email_data):
        self.logger.info("SemanticAgent execution started.")
        risk_score = 0
        reasons = []
        body = email_data.get('body', "")

        # 1. Fast Keyword Check
        intent_res = infer_intent(body)
        if intent_res:
            risk_score += intent_res.get('severity', 0)
            reasons.append(f"Keyword: {intent_res.get('reason')}")

        # 2. AI Model Check
        if self.use_ai and body:
            try:
                self._load_model()
                inputs = self.tokenizer(body, return_tensors="pt", truncation=True, max_length=512)
                with torch.no_grad():
                    outputs = self.model(**inputs)
                
                # Assuming index 1 is phishing/malicious based on typical binary classification
                # We need to verify the model's label map, but usually 1 = Phishing
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
                phishing_prob = probabilities[0][1].item()
                
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
