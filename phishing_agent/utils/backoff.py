import time
import functools
import random
from googleapiclient.errors import HttpError
import logging

def exponential_backoff(max_retries=5, base_delay=2, max_delay=60):
    """
    Decorator to apply exponential backoff to a function.
    Catches HttpError and retries if appropriate.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            retries = 0
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except HttpError as e:
                    # Retry on 429 (Too Many Requests) or 5xx (Server Errors)
                    if e.resp.status in [429, 500, 502, 503, 504]:
                        retries += 1
                        if retries >= max_retries:
                            raise e
                        
                        # Add jitter to prevent thundering herd
                        sleep_time = min(delay, max_delay) + random.uniform(0, 1)
                        logging.getLogger("PhishingAgent").warning(f"API Error {e.resp.status}: Retrying in {sleep_time:.2f}s...")
                        time.sleep(sleep_time)
                        delay *= 2
                    else:
                        # Don't retry client errors (400, 401, 403, 404)
                        raise e
            return func(*args, **kwargs)
        return wrapper
    return decorator
