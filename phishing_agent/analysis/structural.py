import re

def extract_urls(text):
    """Robust URL extraction[cite: 48]."""
    if not text: return []
    # Regex to capture http/https links
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return list(set(url_pattern.findall(text)))