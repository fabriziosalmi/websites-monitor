import requests

def check_domain_breach(website):
    domain_breach = "🟢"  # Start with a default "safe" status.
    
    try:
        breach_url = f"https://breachdirectory.com/api/domain/{website}"
        response = requests.get(breach_url)
        
        if response.status_code != 200:
            print(f"Error occurred while fetching breach data for {website}. Status Code: {response.status_code}")
            domain_breach = "🔘"  # Assume "grey" due to an API error.
        else:
            data = response.json()
            
            # If the domain was found in any breaches, set the status to "red".
            if data.get('found') and data['found'] == True:
                domain_breach = "🔴"
        
    except Exception as e:
        print(f"An error occurred while checking breach data for {website}: {e}")
        domain_breach = "🔘"  # Set "grey" due to a processing error.

    return domain_breach
