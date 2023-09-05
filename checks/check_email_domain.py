import dns.resolver

def check_email_domain(email_domain):
    try:
        answers = dns.resolver.resolve(email_domain, 'TXT')
        for rdata in answers:
            if "v=spf1" in str(rdata):
                return "🟢"
        return "🔴"
    except Exception as e:
        print(f"An error occurred while checking email domain for {email_domain}: {e}")
        return "🔴"
