import requests

def check_asset_minification(website_links):
    minified_count = 0
    total_assets = 0
    
    for link in website_links:
        try:
            response = requests.get(link)
            
            # Check if the content type is either CSS or JavaScript
            content_type = response.headers.get('Content-Type', '')
            if 'text/css' in content_type or 'application/javascript' in content_type:
                total_assets += 1
                content = response.text
                if len(content) != len(content.strip()):
                    # Content is not minified
                    continue
                minified_count += 1

        except Exception as e:
            print(f"Error fetching content from {link}: {e}")
    
    if total_assets == 0:
        return "⚪"  # No assets to check
    elif minified_count == 0:
        return "🔴"  # None of the assets are minified
    elif minified_count < total_assets:
        return "🟠"  # Some assets are minified, others are not
    else:
        return "🟢"  # All assets are minified
