import requests

def check_domainsblacklists_blacklist(domain):
    url = "https://get.domainsblacklists.com/blacklist.txt"

    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        # We'll use an iterative approach to prevent loading the entire list into memory.
        # This will search the file line by line.
        for line in response.iter_lines(decode_unicode=True):
            if line.strip() == domain:
                return "🔴"
        return "🟢"
    except requests.RequestException:
        return "⚪"  # Return gray if there's an error in fetching or processing.

# Example usage
print(check_domainsblacklists_blacklist("example.com"))
