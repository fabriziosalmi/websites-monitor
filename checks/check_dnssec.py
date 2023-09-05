import dns.resolver

def check_dnssec(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A', check_origin=True)
        return "🟢"
    except dns.resolver.NoAnswer:
        return "🔴"
    except Exception as e:
        print(f"An error occurred while checking DNSSEC for {domain}: {e}")
        return "🔴"
