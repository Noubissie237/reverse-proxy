#!/usr/bin/env python3
"""
DNS Configuration Checker for SSL Certificate Installation
Version améliorée avec vérification du domaine principal et www
"""
import socket
import requests
import sys

def get_server_ip():
    """Get current server's public IP address"""
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text.strip()
    except requests.Timeout:
        print(f"❌ Timeout while getting server IP (network may be slow)")
        return None
    except Exception as e:
        print(f"❌ Failed to get server IP: {e}")
        return None

def get_domain_ip(domain):
    """Get IP address that domain resolves to"""
    try:
        # Set timeout for DNS resolution
        socket.setdefaulttimeout(10)
        ip = socket.gethostbyname(domain)
        socket.setdefaulttimeout(None)  # Reset to default
        return ip
    except socket.timeout:
        print(f"❌ Timeout while resolving {domain} (DNS may be slow)")
        socket.setdefaulttimeout(None)  # Reset to default
        return None
    except Exception as e:
        print(f"❌ Failed to resolve {domain}: {e}")
        socket.setdefaulttimeout(None)  # Reset to default
        return None

def get_both_domains(input_domain):
    """Extract both main domain and www version from input"""
    if input_domain.startswith('www.'):
        main_domain = input_domain[4:]  # Remove www.
        www_domain = input_domain
    else:
        main_domain = input_domain
        www_domain = f"www.{input_domain}"
    
    return main_domain, www_domain

def check_single_domain(domain, server_ip, step_name):
    """Check if a single domain points to the server"""
    print(f"\n📋 {step_name}: Checking {domain}...")
    
    domain_ip = get_domain_ip(domain)
    
    if not domain_ip:
        print(f"❌ {domain} could not be resolved")
        print(f"💡 Create a DNS A record for {domain} pointing to {server_ip}")
        return False
    
    print(f"🌐 {domain} IP: {domain_ip}")
    
    if server_ip != domain_ip:
        print(f"❌ {domain} does not point to this server")
        print(f"💡 Update your DNS A record for {domain} to point to {server_ip}")
        return False
    
    print(f"✅ {domain} correctly points to this server!")
    return True

def check_domain_dns_complete(input_domain):
    """Check if both main domain and www subdomain DNS point to current server"""
    main_domain, www_domain = get_both_domains(input_domain)
    
    print(f"🔍 Checking DNS configuration for both {main_domain} and {www_domain}...")
    
    server_ip = get_server_ip()
    if not server_ip:
        return False
    
    print(f"🌐 Server IP: {server_ip}")
    
    # Checking for main domain
    main_success = check_single_domain(main_domain, server_ip, "Step 1")
    
    # Checking for www version
    www_success = check_single_domain(www_domain, server_ip, "Step 2")
    
    return main_success and www_success

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 check_dns.py <domain>")
        print("Example: python3 check_dns.py mysite.com")
        print("Example: python3 check_dns.py www.mysite.com")
        print("Example: python3 check_dns.py first.example.com")
        sys.exit(1)
    
    input_domain = sys.argv[1].strip()
    main_domain, www_domain = get_both_domains(input_domain)
    
    success = check_domain_dns_complete(input_domain)
    
    if success:
        print(f"\n🎉 Both {main_domain} and {www_domain} are ready for SSL certificate installation!")
        print("✅ DNS configuration is complete!")
    else:
        print(f"\n⚠️  DNS configuration is not complete for SSL certificate installation")
        print("📝 Please update your DNS settings as indicated above and try again.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()