import dns.resolver

def check_dns_blacklist(domain):
    blacklists = ["zen.spamhaus.org", "bl.spamcop.net"]
    for blacklist in blacklists:
        try:
            dns.resolver.query(f"{domain}.{blacklist}", 'A')
            return "🔴"
        except:
            continue
    return "🟢"
