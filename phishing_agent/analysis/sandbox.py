import socket
import requests
import urllib.parse
from config import DNS_TIMEOUT, HTTP_TIMEOUT

def check_dns_redirects(url):
    """Checks DNS existence and redirect depth[cite: 30, 49]."""
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        if not domain: return None

        # Unified Check using Requests with strict timeout
        # This implicitly checks DNS and avoids hanging on 'tarpits'
        try:
            response = requests.head(url, timeout=HTTP_TIMEOUT, allow_redirects=True)
            if len(response.history) > 2:
                return {"severity": 50, "reason": "Excessive Redirects", "detail": f"Depth: {len(response.history)}"}
        
        except requests.exceptions.ConnectionError as e:
            # Inspect error to distinguish DNS failure from other connection errors
            err_str = str(e).lower()
            if "name or service not known" in err_str or "getaddrinfo failed" in err_str:
                return {"severity": 30, "reason": "Unresolvable Domain", "detail": domain}
        except requests.exceptions.Timeout:
            # Timeout means server is unresponsive or tarpitting; we fail safe/silent here
            pass
        except requests.RequestException:
            pass 

    except Exception:
        pass
    return None