#!/usr/bin/env python3
"""
DNS Configuration Checker for SSL Certificate Installation
"""

import socket
import requests
import sys

def get_server_ip():
    """Get current server's public IP address"""
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Failed to get server IP: {e}")
        return None

def get_domain_ip(domain):
    """Get IP address that domain resolves to"""
    try:
        return socket.gethostbyname(domain)
    except Exception as e:
        print(f"❌ Failed to resolve {domain}: {e}")
        return None

def check_domain_dns(domain):
    """Check if domain DNS points to current server"""
    print(f"🔍 Checking DNS configuration for {domain}...")
    
    server_ip = get_server_ip()
    if not server_ip:
        return False
    
    domain_ip = get_domain_ip(domain)
    if not domain_ip:
        return False
    
    print(f"🌐 Server IP: {server_ip}")
    print(f"🌐 Domain IP: {domain_ip}")
    
    if server_ip == domain_ip:
        print(f"✅ {domain} correctly points to this server!")
        return True
    else:
        print(f"❌ {domain} does not point to this server")
        print(f"💡 Update your DNS A record to point to {server_ip}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 check_dns.py <domain>")
        print("Example: python3 check_dns.py mysite.com")
        sys.exit(1)
    
    domain = sys.argv[1]
    success = check_domain_dns(domain)
    
    if success:
        print(f"\n🎉 {domain} is ready for SSL certificate installation!")
    else:
        print(f"\n⚠️  {domain} is not ready for SSL certificate installation")
        print("Please update your DNS settings and try again.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
