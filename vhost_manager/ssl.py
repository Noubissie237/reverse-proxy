"""
SSL certificate management (standard and wildcard)
"""
import os
import socket
import requests
import logging
from .validation import get_validated_email, get_base_domain
from .utils import run_command

logger = logging.getLogger(__name__)


def check_domain_dns(domain):
    """
    Check if domain DNS points to current server
    
    Args:
        domain (str): Domain name to check
        
    Returns:
        bool: True if DNS points to current server, False otherwise
    """
    try:
        # Add timeout to prevent hanging
        current_ip = requests.get('https://api.ipify.org', timeout=10).text
        # Set socket timeout for DNS resolution
        socket.setdefaulttimeout(10)
        domain_ip = socket.gethostbyname(domain)
        socket.setdefaulttimeout(None)  # Reset to default
        return domain_ip == current_ip
    except requests.Timeout:
        logger.error(f"Timeout while checking server IP")
        return False
    except socket.timeout:
        logger.error(f"Timeout while resolving domain {domain}")
        return False
    except Exception as e:
        logger.error(f"Failed to check domain DNS: {e}")
        return False


def install_ssl_certificate(domain):
    """
    Install SSL certificate using Let's Encrypt
    
    Args:
        domain (str): Domain name for SSL certificate
        
    Returns:
        bool: True if certificate was installed successfully
    """
    print(f"🔒 Installing SSL certificate for {domain}...")
    
    # Check if certbot is installed
    if not run_command("which certbot"):
        print("📦 Certbot not found. Installing Certbot...")
        if not run_command("apt update && apt install -y certbot python3-certbot-apache"):
            print("❌ Failed to install Certbot")
            return False
    
    # Check if domain DNS points to current server
    print("🔍 Checking domain DNS configuration...")
    if not check_domain_dns(domain):
        print(f"⚠️  Warning: Domain {domain} may not point to this server")
        print("💡 Make sure your DNS A record points to this server's IP address")
        response = input("Continue with SSL installation anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
    # Create temporary HTTP-only virtual host for Let's Encrypt challenge
    print("🔧 Creating temporary HTTP configuration for Let's Encrypt verification...")
    temp_config = f"""<VirtualHost *:80>
    ServerName {domain}
    ServerAlias www.{domain}
    
    # Document root for Let's Encrypt challenges
    DocumentRoot /var/www/html
    
    # Allow .well-known directory for Let's Encrypt
    <Directory "/var/www/html/.well-known">
        AllowOverride None
        Require all granted
    </Directory>
    
    # Logging
    ErrorLog ${{APACHE_LOG_DIR}}/{domain}-error.log
    CustomLog ${{APACHE_LOG_DIR}}/{domain}-access.log combined
</VirtualHost>"""
    
    temp_config_path = f"/etc/apache2/sites-available/{domain}-temp.conf"
    try:
        with open(temp_config_path, 'w') as f:
            f.write(temp_config)
        
        # Disable existing site and enable temporary one
        run_command(f"a2dissite {domain}.conf", show_output=False)
        run_command(f"a2ensite {domain}-temp.conf")
        run_command("systemctl reload apache2")
        
    except Exception as e:
        print(f"❌ Failed to create temporary configuration: {e}")
        return False
    
    # Get SSL certificate
    certbot_cmd = f"certbot --apache -d {domain} -d www.{domain} --non-interactive --agree-tos"
    
    # Get validated email
    email = get_validated_email()
    certbot_cmd += f" --email {email}"
    
    # Run certbot
    success = run_command(certbot_cmd, show_output=True)
    
    # Clean up temporary configuration
    run_command(f"a2dissite {domain}-temp.conf", show_output=False)
    if os.path.exists(temp_config_path):
        os.remove(temp_config_path)
    
    if success:
        print("✅ SSL certificate installed successfully!")
        print("🔄 Automatic renewal is configured")
        logger.info(f"SSL certificate installed for {domain}")
        return True
    else:
        print("❌ Failed to install SSL certificate")
        print("💡 Make sure your DNS points to this server and port 80/443 are accessible")
        print("💡 Verify that your domain actually resolves to this server's IP address")
        logger.error(f"SSL certificate installation failed for {domain}")
        return False


def install_wildcard_ssl_certificate(domain):
    """
    Install wildcard SSL certificate using Let's Encrypt DNS-01 challenge
    
    Args:
        domain (str): Wildcard domain name (e.g., *.example.com)
        
    Returns:
        bool: True if certificate was installed successfully
    """
    base_domain = get_base_domain(domain)
    
    print(f"\n🌟 Installing Wildcard SSL certificate for {domain}")
    print("=" * 70)
    
    # Check if certbot is installed
    if not run_command("which certbot"):
        print("📦 Certbot not found. Installing Certbot...")
        if not run_command("apt update && apt install -y certbot"):
            print("❌ Failed to install Certbot")
            return False
    
    # Get validated email
    email = get_validated_email()
    
    print("\n📋 Wildcard Certificate Information:")
    print(f"   Domain: {domain}")
    print(f"   Base Domain: {base_domain}")
    print(f"   Email: {email}")
    print(f"   Challenge Type: DNS-01 (manual)")
    print()
    
    print("⚠️  IMPORTANT: Wildcard certificates require DNS validation")
    print("   You will need to add a TXT record to your DNS configuration.")
    print()
    
    response = input("Ready to proceed? (y/n): ")
    if response.lower() != 'y':
        print("❌ Wildcard SSL installation cancelled")
        return False
    
    # Build certbot command for manual DNS challenge
    certbot_cmd = (
        f"certbot certonly --manual "
        f"--preferred-challenges dns "
        f"-d {domain} "
        f"-d {base_domain} "
        f"--email {email} "
        f"--agree-tos "
        f"--no-eff-email"
    )
    
    print("\n🔧 Starting certbot with DNS challenge...")
    print("=" * 70)
    print()
    print("📝 INSTRUCTIONS:")
    print("   1. Certbot will provide a TXT record value")
    print("   2. Add this TXT record to your DNS:")
    print(f"      Name: _acme-challenge.{base_domain}")
    print("      Type: TXT")
    print("      Value: [provided by certbot]")
    print()
    print("   3. Wait 1-5 minutes for DNS propagation")
    print("   4. You can verify propagation with:")
    print(f"      dig _acme-challenge.{base_domain} TXT")
    print()
    print("   5. Press Enter in certbot when ready")
    print()
    print("=" * 70)
    print()
    
    input("Press Enter to start certbot (Ctrl+C to cancel)...")
    
    # Run certbot interactively
    success = run_command(certbot_cmd, show_output=True)
    
    if success:
        print("\n✅ Wildcard SSL certificate installed successfully!")
        print(f"📁 Certificate location: /etc/letsencrypt/live/{base_domain}/")
        print("🔄 Automatic renewal is configured")
        print()
        print(f"💡 This certificate covers:")
        print(f"   - {domain} (all subdomains)")
        print(f"   - {base_domain} (base domain)")
        print()
        logger.info(f"Wildcard SSL certificate installed for {domain}")
        return True
    else:
        print("\n❌ Failed to install wildcard SSL certificate")
        print()
        print("💡 Troubleshooting:")
        print("   - Verify the TXT record was added correctly")
        print("   - Wait longer for DNS propagation (up to 15 minutes)")
        print(f"   - Check DNS with: dig _acme-challenge.{base_domain} TXT")
        print("   - Ensure you have access to modify DNS records")
        print()
        logger.error(f"Wildcard SSL certificate installation failed for {domain}")
        return False


def renew_ssl_certificates():
    """Renew all SSL certificates"""
    print("🔄 Renewing SSL certificates...")
    
    if run_command("certbot renew --quiet"):
        print("✅ SSL certificates renewed")
        run_command("systemctl reload apache2")
        logger.info("SSL certificates renewed successfully")
    else:
        print("❌ Failed to renew SSL certificates")
        logger.error("SSL certificate renewal failed")
