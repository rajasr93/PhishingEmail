def analyze_headers(headers_dict):
    """Checks for Reply-To mismatches and Auth failures."""
    risks = []
    
    # 1. Reply-To Mismatch
    from_addr = headers_dict.get('From', '')
    reply_to = headers_dict.get('Reply-To', '')
    
    if reply_to and from_addr:
        if extract_domain(from_addr) != extract_domain(reply_to):
            risks.append({
                "severity": 70, 
                "reason": "Reply-To Mismatch",
                "detail": f"From: {from_addr} | Reply-To: {reply_to}"
            })

    # 2. Auth Check (SPF/DKIM/DMARC signals) [cite: 50]
    auth_results = headers_dict.get('Authentication-Results', '').lower()
    if 'spf=fail' in auth_results or 'dkim=fail' in auth_results:
        risks.append({
            "severity": 90, 
            "reason": "Authentication Failed",
            "detail": "SPF/DKIM check failed"
        })

    return risks

def extract_domain(email):
    try:
        return email.split('@')[-1].strip().lower().replace('>', '')
    except:
        return ""