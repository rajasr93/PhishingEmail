import re
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normalizes text to remove obfuscation attempts.
    1. Unicode Normalization (NFKC) to convert homoglyphs/styled text.
    2. Removal of zero-width characters.
    3. Whitespace collapsing.
    """
    if not text:
        return ""
    
    # Normalize unicode (e.g., 𝐇𝐞𝐥𝐥𝐨 -> Hello)
    text = unicodedata.normalize('NFKC', text)
    
    # Remove zero-width spaces and other invisible formatting characters
    # \u200b: Zero width space
    # \u200c: Zero width non-joiner
    # \u200d: Zero width joiner
    # \u2060: Word joiner
    # \ufeff: Zero width no-break space
    text = re.sub(r'[\u200b\u200c\u200d\u2060\ufeff]', '', text)
    
    # Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip().lower()

class IntentScanner:
    """
    Regex-based scanner for detecting specific threat indicators in text.
    """
    def __init__(self):
        # Dictionary of threat categories and their regex patterns
        # Using \b word boundaries is crucial to avoid partial matches
        self.patterns = {
            "Urgency": {
                "patterns": [
                    r"\b(urgent|immediate|immediately|critical|24\s*hours|48\s*hours)\b",
                    r"\b(suspend|terminate|restrict|lock|blocked|expire|closing)\b",
                    r"\b(act\s+now|action\s+required|final\s+notice|deletion)\b"
                ],
                "severity": 40,
                "msg": "High Urgency Detected"
            },
            "Credential_Theft": {
                "patterns": [
                    r"\b(password|login|verify\s+account|update\s+details|confirm\s+identity)\b",
                    r"\b(click\s+here|sign\s+in|validate|unusual\s+activity)\b",
                    r"\b(reactivate|secure\s+your\s+account)\b"
                ],
                "severity": 40,
                "msg": "Credential Harvesting Pattern"
            },
            "Financial": {
                "patterns": [
                    r"\b(bank|transfer|invoice|payment|account\s+details|bitcoin|wallet)\b",
                    r"\b(overdue|unpaid|refund|wire)\b"
                ],
                "severity": 20,
                "msg": "Financial/Payment Request"
            }
        }
        
        # Pre-compile patterns
        self.compiled_patterns = {}
        for key, data in self.patterns.items():
            self.compiled_patterns[key] = [re.compile(p, re.IGNORECASE) for p in data["patterns"]]

    def scan(self, text: str):
        """
        Scans normalized text for all threat categories.
        Returns (total_score, list_of_reasons)
        """
        total_score = 0
        reasons = []
        
        for category, data in self.patterns.items():
            matched = False
            for pattern in self.compiled_patterns[category]:
                if pattern.search(text):
                    matched = True
                    break # Stop checking other patterns in this category if one matches
            
            if matched:
                total_score += data["severity"]
                reasons.append(f"{data['msg']} ({category})")
                
        return total_score, reasons
