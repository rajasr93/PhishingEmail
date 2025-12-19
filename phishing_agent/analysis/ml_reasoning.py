def infer_intent(text):
    """Heuristic check for Urgency and BEC patterns[cite: 37, 51]."""
    text = text.lower() if text else ""
    urgency_words = ['urgent', 'immediate', '24 hours', 'suspend']
    credential_words = ['password', 'login', 'verify account']
    
    if any(w in text for w in urgency_words):
        return {"severity": 40, "reason": "Urgency Detected", "detail": "High urgency keywords"}
    
    if any(w in text for w in credential_words):
        return {"severity": 40, "reason": "Credential Request", "detail": "Login keywords"}
        
    return None