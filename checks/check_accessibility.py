import requests
import re
from requests.exceptions import RequestException, Timeout, HTTPError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_accessibility(website):
    """
    Check the website's accessibility score using Lighthouse or similar services.
    
    Args:
    - website (str): URL of the website to be checked.
    
    Returns:
    - str: "🟢" if the accessibility score is high (0.9 to 1),
           "🟠" if the score is moderate (0.8 to 0.9),
           "🔴" if the score is low (less than 0.8),
           "⚪" for any errors.
    """
    # Input validation and URL normalization
    if not website or not isinstance(website, str):
        logger.error(f"Invalid website input: {website}")
        return "⚪"
    
    website = website.strip()
    if not website.startswith(('http://', 'https://')):
        website = f"https://{website}"

    LIGHTHOUSE_API_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    WAVE_API_ENDPOINT = "https://wave.webaim.org/api/request"
    
    # Enhanced regex patterns for comprehensive accessibility checks
    accessibility_patterns = {
        'alt_text': re.compile(r'<img[^>]+alt\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
        'aria_roles': re.compile(r'role\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
        'aria_labels': re.compile(r'aria-label\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
        'aria_describedby': re.compile(r'aria-describedby\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
        'language_attr': re.compile(r'<html[^>]+lang\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
        'heading_structure': re.compile(r'<h[1-6][^>]*>', re.IGNORECASE),
        'form_labels': re.compile(r'<label[^>]*for\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
        'input_labels': re.compile(r'<input[^>]+aria-label\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
        'skip_links': re.compile(r'href\s*=\s*["\']#[^"\']*["\'][^>]*>skip', re.IGNORECASE),
        'focus_indicators': re.compile(r':focus\s*{[^}]*outline', re.IGNORECASE),
        'empty_alt': re.compile(r'<img[^>]+alt\s*=\s*["\']["\']', re.IGNORECASE),
        'missing_alt': re.compile(r'<img(?![^>]*alt\s*=)', re.IGNORECASE),
    }

    lighthouse_params = {
        "url": website,
        "category": "accessibility",
        "strategy": "desktop"
    }

    headers = {'User-Agent': 'AccessibilityChecker/1.0'}

    try:
        response = requests.get(LIGHTHOUSE_API_ENDPOINT, params=lighthouse_params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        score = data['lighthouseResult']['categories']['accessibility']['score']
        logger.info(f"Lighthouse accessibility score for {website}: {score}")
        
        if score >= 0.9:
            return "🟢"
        elif 0.8 <= score < 0.9:
            return "🟠"
        else:
            return "🔴"

    except (Timeout, HTTPError, RequestException) as e:
        logger.warning(f"Lighthouse API failed for {website}: {e}")
        
        # Fallback to WAVE API (if API key is available)
        wave_params = {
            "key": "YOUR_WAVE_API_KEY",
            "url": website,
            "reporttype": "json"
        }
        try:
            wave_response = requests.get(WAVE_API_ENDPOINT, params=wave_params, headers=headers, timeout=15)
            wave_response.raise_for_status()
            wave_data = wave_response.json()
            errors_count = wave_data['categories']['error']['count']
            logger.info(f"WAVE accessibility errors for {website}: {errors_count}")
            
            if errors_count == 0:
                return "🟢"
            elif 1 <= errors_count <= 10:
                return "🟠"
            else:
                return "🔴"

        except (Timeout, HTTPError, RequestException) as e:
            logger.warning(f"WAVE API failed for {website}: {e}")
            
            # Enhanced manual heuristic accessibility check
            try:
                response = requests.get(website, headers=headers, timeout=15)
                response.raise_for_status()
                content = response.text.lower()  # Case-insensitive matching
                
                # Calculate weighted accessibility score
                score_components = {
                    'alt_text': _check_images_accessibility(content, accessibility_patterns),
                    'aria_support': _check_aria_support(content, accessibility_patterns),
                    'language_attr': bool(accessibility_patterns['language_attr'].search(content)),
                    'heading_structure': _check_heading_structure(content, accessibility_patterns),
                    'form_accessibility': _check_form_accessibility(content, accessibility_patterns),
                    'navigation_support': bool(accessibility_patterns['skip_links'].search(content)),
                    'focus_management': bool(accessibility_patterns['focus_indicators'].search(content)),
                }
                
                # Weighted scoring system
                weights = {
                    'alt_text': 0.25,
                    'aria_support': 0.20,
                    'language_attr': 0.15,
                    'heading_structure': 0.15,
                    'form_accessibility': 0.15,
                    'navigation_support': 0.05,
                    'focus_management': 0.05,
                }
                
                total_score = sum(score_components[key] * weights[key] for key in weights)
                logger.info(f"Manual accessibility score for {website}: {total_score:.2f}")
                logger.debug(f"Score components: {score_components}")
                
                if total_score >= 0.8:
                    return "🟢"
                elif total_score >= 0.6:
                    return "🟠"
                else:
                    return "🔴"

            except Exception as e:
                logger.error(f"Error during manual heuristic accessibility check for {website}: {e}")
                return "⚪"

def _check_images_accessibility(content, patterns):
    """Check image accessibility with alt text."""
    images_with_alt = len(patterns['alt_text'].findall(content))
    images_missing_alt = len(patterns['missing_alt'].findall(content))
    empty_alt_images = len(patterns['empty_alt'].findall(content))
    
    total_images = images_with_alt + images_missing_alt
    if total_images == 0:
        return 1.0  # No images, so no accessibility issues
    
    # Penalize missing alt text more than empty alt text (which might be decorative)
    good_images = images_with_alt - empty_alt_images * 0.5
    return max(0, good_images / total_images)

def _check_aria_support(content, patterns):
    """Check ARIA attributes usage."""
    aria_features = [
        patterns['aria_roles'].search(content),
        patterns['aria_labels'].search(content),
        patterns['aria_describedby'].search(content),
    ]
    return sum(bool(feature) for feature in aria_features) / len(aria_features)

def _check_heading_structure(content, patterns):
    """Check for proper heading structure."""
    headings = patterns['heading_structure'].findall(content)
    if not headings:
        return 0.5  # Neutral score if no headings found
    
    # Basic check: if headings exist, assume some structure
    return 1.0 if len(headings) > 0 else 0.0

def _check_form_accessibility(content, patterns):
    """Check form accessibility with labels."""
    form_labels = len(patterns['form_labels'].findall(content))
    input_labels = len(patterns['input_labels'].findall(content))
    
    # If no forms detected, return neutral score
    if '<form' not in content and '<input' not in content:
        return 1.0
    
    # Simple heuristic: presence of labels indicates better accessibility
    return 1.0 if (form_labels > 0 or input_labels > 0) else 0.0
