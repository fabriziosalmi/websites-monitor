import re
import requests

def check_privacy_exposure(website):
    """
    Check a given website for potential exposure of sensitive or private data.
    
    Args:
    - website (str): The URL of the website to be checked.
    
    Returns:
    - str: "🟢" if no patterns of sensitive data are found, "🔴" otherwise.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(f"https://{website}", headers=headers)
        # Patterns:
        # 1. Email addresses
        # 2. 10-digit numbers (e.g., phone numbers)
        # 3. Credit Card numbers (XXXX-XXXX-XXXX-XXXX or XXXXXXXXXXXXXXXX)
        # 4. Social Security Numbers (XXX-XX-XXXX)
        sensitive_data_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', 
            r'\b\d{10}\b',
            r'(\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b)',  
            r'(\b\d{3}[- ]?\d{2}[- ]?\d{4}\b)'  # This might detect more than just SSNs, use cautiously
        ]

        for pattern in sensitive_data_patterns:
            if re.search(pattern, response.text, re.IGNORECASE):
                return "🔴"

        return "🟢"
    except Exception as e:
        print(f"An error occurred while checking for privacy exposure on {website}: {e}")
        return "⚪"
