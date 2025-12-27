import requests
import warnings
from requests.exceptions import RequestException, Timeout, HTTPError

# Suppress warnings if necessary, but usually better to handle them.
# warnings.filterwarnings("ignore")

def fetch_page(url, retries=3, timeout=10):
    """
    Fetches HTML content from a given URL with robust error handling.
    
    Args:
        url (str): The URL to fetch.
        retries (int): Number of retries for failed requests.
        timeout (int): Timeout in seconds for the request.
        
    Returns:
        str or None: Raw HTML content if successful, None otherwise.
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx, 5xx)
            return response.text
            
        except Timeout:
            print(f"[Warning] Timeout fetching {url} (Attempt {attempt + 1}/{retries})")
        except HTTPError as e:
            print(f"[Error] HTTP error fetching {url}: {e}")
            # usually 404s etc shouldn't be retried blindly, but for flakey servers maybe.
            # breaking here as 404 won't likely change on retry immediately
            break 
        except RequestException as e:
            print(f"[Error] Request failed for {url}: {e}")
            
        # Exponential backoff or simple sleep could be added here
        # time.sleep(1) 
        
    print(f"[Failed] Could not fetch {url} after {retries} attempts.")
    return None
