import time
from config import HIGH_RISK_THRESHOLD
from .headers import analyze_headers
from .structural import extract_urls
from .sandbox import check_dns_redirects
from .ml_reasoning import infer_intent

def analyze_email_content(email_data):
    """
    Aggregates risks using 'Worst-Link Elevation'.
    Includes Early-Exit logic for high-confidence signals.
    """
    start_time = time.time()
    risks = []
    
    # 1. Header Analysis 
    # v1 Update: Use dedicated AuthValidator
    from auth_validator import AuthValidator
    validator = AuthValidator()
    auth_score, auth_reasons = validator.validate(email_data)
    
    if auth_score > 0:
        for reason in auth_reasons:
            risks.append({
                "severity": auth_score, # Use the raw score from validator
                "reason": "Authentication Failure",
                "detail": reason
            })
    
    # Also check other headers (Reply-To mismatch)
    header_risks = analyze_headers(email_data.get('headers', {}))
    if header_risks: 
        risks.extend(header_risks)

    # Check for Early Exit
    if any(r['severity'] >= HIGH_RISK_THRESHOLD for r in risks):
        return _finalize_report(risks, start_time, "Early Exit: High Risk Header")

    # 2. Structural & URL Analysis [cite: 48]
    body_content = email_data.get('body', "")
    urls = extract_urls(body_content)
    
    # 3. Sandbox Analysis (Network) [cite: 49]
    # This is the most expensive step, so we exit before this if possible.
    for url in urls:
        network_risk = check_dns_redirects(url)
        if network_risk: 
            risks.append(network_risk)
            # Early Exit on confirmed malicious network signal
            if network_risk['severity'] >= HIGH_RISK_THRESHOLD:
                return _finalize_report(risks, start_time, "Early Exit: Malicious Network Artifact")

    # 4. Semantic Reasoning [cite: 51]
    intent_risk = infer_intent(body_content)
    if intent_risk: risks.append(intent_risk)

    return _finalize_report(risks, start_time, "Full Scan Complete")

def _finalize_report(risks, start_time, status_note):
    """Helper to calculate final score based on Worst-Link Elevation."""
    final_score = 0
    primary_reason = "Clean"
    
    if risks:
        risks.sort(key=lambda x: x['severity'], reverse=True)
        worst_risk = risks[0]
        final_score = worst_risk['severity']
        primary_reason = worst_risk['reason']

    return {
        "score": final_score,
        "primary_reason": primary_reason,
        "details": risks,
        "scan_status": status_note,
        "duration": round(time.time() - start_time, 3)
    }