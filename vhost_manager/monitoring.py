"""
Monitoring functions for Virtual Hosts (status, SSL checks, statistics)
"""
import os
import socket
import subprocess
import logging
from datetime import datetime
from OpenSSL import crypto

logger = logging.getLogger(__name__)


def check_port_in_use(port):
    """
    Check if a port is in use
    
    Args:
        port (int): Port number to check
        
    Returns:
        bool: True if port is in use, False otherwise
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        # connect_ex returns 0 if connection succeeds (port in use)
        # returns non-zero if connection fails (port available)
        result = s.connect_ex(('localhost', port))
        s.close()
        return result == 0  # Port is in use if connection succeeds
    except Exception:
        return False


def check_site_status(domain, sites):
    """
    Check the status of a specific site
    
    Args:
        domain (str): Domain name to check
        sites (dict): Sites configuration
        
    Returns:
        dict: Status information
    """
    status = {
        'domain': domain,
        'apache_enabled': False,
        'port_active': False,
        'ssl_enabled': False,
        'ssl_valid': False,
        'ssl_days_remaining': None
    }
    
    if domain not in sites:
        return status
    
    site_config = sites[domain]
    port = site_config['port']
    
    # Check if Apache site is enabled
    result = subprocess.run(
        f"a2query -s {domain}.conf",
        shell=True,
        capture_output=True,
        text=True
    )
    status['apache_enabled'] = result.returncode == 0
    
    # Check if port is active
    status['port_active'] = check_port_in_use(port)
    
    # Check SSL status
    status['ssl_enabled'] = site_config.get('ssl', False)
    
    if status['ssl_enabled']:
        ssl_info = get_ssl_certificate_info(domain)
        if ssl_info:
            status['ssl_valid'] = ssl_info['valid']
            status['ssl_days_remaining'] = ssl_info['days_remaining']
    
    return status


def get_ssl_certificate_info(domain):
    """
    Get SSL certificate information for a domain
    
    Args:
        domain (str): Domain name
        
    Returns:
        dict: Certificate information or None
    """
    cert_path = f"/etc/letsencrypt/live/{domain}/cert.pem"
    
    if not os.path.exists(cert_path):
        return None
    
    try:
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
        
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
        
        # Get expiration date
        expiry_date_str = cert.get_notAfter().decode('utf-8')
        expiry_date = datetime.strptime(expiry_date_str, '%Y%m%d%H%M%SZ')
        
        # Calculate days remaining
        days_remaining = (expiry_date - datetime.now()).days
        
        return {
            'valid': days_remaining > 0,
            'expiry_date': expiry_date,
            'days_remaining': days_remaining,
            'issuer': cert.get_issuer().CN
        }
    except Exception as e:
        logger.error(f"Failed to read SSL certificate for {domain}: {e}")
        return None


def show_status(sites):
    """Show detailed status of all sites"""
    if not sites:
        print("📝 No sites configured")
        return
    
    print("\n" + "=" * 80)
    print("📊 SITES STATUS REPORT")
    print("=" * 80 + "\n")
    
    for domain in sorted(sites.keys()):
        status = check_site_status(domain, sites)
        site_config = sites[domain]
        
        print(f"🌐 {domain}")
        print("─" * 80)
        
        # Apache status
        apache_icon = "✅" if status['apache_enabled'] else "❌"
        print(f"  Apache:     {apache_icon} {'Enabled' if status['apache_enabled'] else 'Disabled'}")
        
        # Port status
        port = site_config['port']
        port_icon = "✅" if status['port_active'] else "⚠️ "
        port_status = "Running" if status['port_active'] else "Not responding"
        print(f"  Port {port}:   {port_icon} {port_status}")
        
        # SSL status
        if status['ssl_enabled']:
            if status['ssl_days_remaining'] is not None:
                days = status['ssl_days_remaining']
                if days > 30:
                    ssl_icon = "✅"
                elif days > 7:
                    ssl_icon = "⚠️ "
                else:
                    ssl_icon = "🔴"
                
                print(f"  SSL:        {ssl_icon} Valid ({days} days remaining)")
            else:
                print(f"  SSL:        ❌ Certificate not found")
        else:
            print(f"  SSL:        ⚪ Not configured")
        
        # Created date
        created = datetime.fromisoformat(site_config['created']).strftime('%Y-%m-%d %H:%M')
        print(f"  Created:    {created}")
        
        # Config file
        print(f"  Config:     {site_config['config_file']}")
        
        print()
    
    print("=" * 80 + "\n")


def check_ssl_certificates(sites):
    """Check all SSL certificates and show expiration info"""
    ssl_sites = {domain: config for domain, config in sites.items() 
                 if config.get('ssl', False)}
    
    if not ssl_sites:
        print("📝 No sites with SSL configured")
        return
    
    print("\n" + "=" * 80)
    print("🔒 SSL CERTIFICATES STATUS")
    print("=" * 80 + "\n")
    
    warnings = []
    errors = []
    
    for domain in sorted(ssl_sites.keys()):
        ssl_info = get_ssl_certificate_info(domain)
        
        if ssl_info is None:
            print(f"❌ {domain:40} Certificate not found")
            errors.append(domain)
            continue
        
        days = ssl_info['days_remaining']
        expiry = ssl_info['expiry_date'].strftime('%Y-%m-%d %H:%M')
        
        if days > 30:
            icon = "✅"
        elif days > 7:
            icon = "⚠️ "
            warnings.append((domain, days))
        elif days > 0:
            icon = "🔴"
            warnings.append((domain, days))
        else:
            icon = "❌"
            errors.append(domain)
        
        print(f"{icon} {domain:40} {days:4} days | Expires: {expiry}")
    
    print("\n" + "=" * 80)
    
    # Summary
    total = len(ssl_sites)
    valid = total - len(warnings) - len(errors)
    
    print(f"\n📊 Summary:")
    print(f"  Total SSL sites:    {total}")
    print(f"  ✅ Valid (>30 days): {valid}")
    print(f"  ⚠️  Warnings:         {len(warnings)}")
    print(f"  ❌ Errors:           {len(errors)}")
    
    if warnings:
        print(f"\n⚠️  Action required for {len(warnings)} certificate(s):")
        for domain, days in warnings:
            print(f"  - {domain}: {days} days remaining")
        print(f"\n💡 Run: sudo python3 manage.py renew-ssl")
    
    if errors:
        print(f"\n❌ Critical issues with {len(errors)} certificate(s):")
        for domain in errors:
            print(f"  - {domain}")
    
    print()


def show_stats(sites):
    """Show statistics about configured sites"""
    if not sites:
        print("📝 No sites configured")
        return
    
    total_sites = len(sites)
    ssl_sites = sum(1 for config in sites.values() if config.get('ssl', False))
    non_ssl_sites = total_sites - ssl_sites
    
    # Count active sites
    active_sites = 0
    for domain in sites.keys():
        status = check_site_status(domain, sites)
        if status['apache_enabled'] and status['port_active']:
            active_sites += 1
    
    print("\n" + "=" * 80)
    print("📈 STATISTICS")
    print("=" * 80 + "\n")
    
    print(f"📊 Total Sites:        {total_sites}")
    print(f"✅ Active Sites:       {active_sites}")
    print(f"⚠️  Inactive Sites:     {total_sites - active_sites}")
    print()
    print(f"🔒 SSL Enabled:        {ssl_sites} ({ssl_sites*100//total_sites if total_sites > 0 else 0}%)")
    print(f"🔓 No SSL:             {non_ssl_sites} ({non_ssl_sites*100//total_sites if total_sites > 0 else 0}%)")
    print()
    
    # Port distribution
    ports = {}
    for config in sites.values():
        port = config['port']
        ports[port] = ports.get(port, 0) + 1
    
    print(f"🔌 Port Distribution:")
    for port, count in sorted(ports.items()):
        print(f"   Port {port:5}: {count} site(s)")
    
    print("\n" + "=" * 80 + "\n")
