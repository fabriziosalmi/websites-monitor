import requests
from requests.exceptions import RequestException, Timeout, HTTPError
import re

def check_asset_minification(website_links):
    """
    Check if the provided website assets (CSS/JS) are minified.

    Args:
        website_links (list): A list of asset URLs (CSS/JS) to be checked.

    Returns:
        str: 
            - "🟢" if all assets are minified
            - "🟠" if some assets are minified and others are not
            - "🔴" if none of the assets are minified
            - "⚪" if an error occurs or no assets to check
    """
    headers = {
        'User-Agent': 'AssetMinificationChecker/1.0'
    }

    minified_count = 0
    total_assets = 0

    try:
        for link in website_links:
            try:
                # Method 1: Check content type and minification status
                response = requests.get(link, headers=headers, timeout=10)
                response.raise_for_status()

                # Check if the content type is either CSS or JavaScript
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/css' in content_type or 'javascript' in content_type:
                    total_assets += 1
                    content = response.text

                    # Basic minification check: Remove whitespace and line breaks
                    minified_content = re.sub(r'\s+', '', content)

                    # Check if the content length is significantly reduced (indicative of minification)
                    if len(minified_content) / len(content) > 0.9:
                        print(f"Asset at {link} is not minified.")
                        continue

                    minified_count += 1

            except (Timeout, HTTPError) as e:
                print(f"Timeout or HTTP error while fetching content from {link}: {e}")
                continue
            except RequestException as e:
                print(f"Request-related error while fetching content from {link}: {e}")
                continue

        # Determine the result based on the minification analysis
        if total_assets == 0:
            print("No assets to check.")
            return "⚪"  # No assets to check
        elif minified_count == 0:
            print("None of the assets are minified.")
            return "🔴"  # None of the assets are minified
        elif minified_count < total_assets:
            print(f"Some assets are minified, others are not. Minified: {minified_count}, Total: {total_assets}")
            return "🟠"  # Some assets are minified, others are not
        else:
            print("All assets are minified.")
            return "🟢"  # All assets are minified

    except Exception as e:
        print(f"An unexpected error occurred while checking asset minification: {e}")
        return "⚪"

    # Method 2: Use heuristic checks for common minification patterns (Fallback)
    try:
        for link in website_links:
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            content = response.text

            # Heuristic: Check for common minification patterns (e.g., lack of line breaks, excessive variable names)
            if re.search(r'(\w)\1{30,}', content):
                print(f"Asset at {link} is likely minified.")
                minified_count += 1
                total_assets += 1

            elif any(line.startswith('//') for line in content.splitlines()):
                print(f"Asset at {link} might not be minified (contains comments).")
                total_assets += 1

        # Determine the result based on the heuristic checks
        if total_assets == 0:
            print("No assets found for heuristic check.")
            return "⚪"
        elif minified_count == 0:
            return "🔴"
        elif minified_count < total_assets:
            return "🟠"
        else:
            return "🟢"

    except (Timeout, HTTPError) as e:
        print(f"Error during heuristic check for minification for {link}: {e}")

    except Exception as e:
        print(f"An unexpected error occurred while checking minification for assets: {e}")

    return "⚪"
