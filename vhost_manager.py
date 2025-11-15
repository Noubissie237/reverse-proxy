#!/usr/bin/env python3

import sys
import os
import json
import logging
import subprocess
import re
import socket
import requests
from pathlib import Path
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
import ssl as ssl_module
from OpenSSL import crypto

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    log_dir = "/var/log/vhost-manager"
    
    # Try to create log directory, fallback to local if permission denied
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_file = f'{log_dir}/manager.log'
    except PermissionError:
        # Fallback to local directory for non-root users
        log_dir = os.path.expanduser("~/.vhost-manager/logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = f'{log_dir}/manager.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class ApacheVHostManager:
    """
    Apache Virtual Host Manager
    
    A comprehensive tool for managing Apache Virtual Hosts with automatic
    SSL certificate installation and configuration.
    """
    
    VERSION = "1.2.0"
    
    def __init__(self):
        self.sites_available = "/etc/apache2/sites-available"
        self.config_file = "/etc/vhost_manager.json"
        self.log_dir = "/var/log/vhost-manager"
        
        # Ensure log directory exists (with fallback for non-root)
        try:
            os.makedirs(self.log_dir, exist_ok=True)
        except PermissionError:
            self.log_dir = os.path.expanduser("~/.vhost-manager/logs")
            os.makedirs(self.log_dir, exist_ok=True)
        
        self.load_config()
    
    def load_config(self):
        """Load existing site configurations from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.sites = json.load(f)
                logger.info(f"Loaded configuration with {len(self.sites)} sites")
            else:
                self.sites = {}
                logger.info("No existing configuration found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.sites = {}
    
    def save_config(self):
        """Save current site configurations to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.sites, f, indent=2)
            
            # Set appropriate permissions
            os.chmod(self.config_file, 0o644)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def check_sudo(self):
        """Verify script is running with sudo privileges"""
        if os.geteuid() != 0:
            print("❌ This script must be run with sudo privileges")
            print("Usage: sudo python3 vhost_manager.py <command> [args]")
            sys.exit(1)
    
    def run_command(self, command, show_output=False, capture_output=True):
        """
        Execute a system command
        
        Args:
            command (str): Command to execute
            show_output (bool): Whether to display command output
            capture_output (bool): Whether to capture command output
            
        Returns:
            bool: True if command succeeded, False otherwise
        """
        try:
            logger.debug(f"Executing command: {command}")
            
            if capture_output:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if show_output:
                    if result.stdout:
                        print(result.stdout)
                    if result.stderr:
                        print(result.stderr)
                
                if result.returncode != 0:
                    logger.warning(f"Command failed with code {result.returncode}: {command}")
                    if result.stderr:
                        logger.warning(f"Error output: {result.stderr}")
                
                return result.returncode == 0
            else:
                # For commands that need interactive input
                result = subprocess.run(command, shell=True)
                return result.returncode == 0
                
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return False
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return False
    
    def create_vhost_config(self, domain, port, use_ssl=True):
        """
        Create Apache Virtual Host configuration file
        
        Args:
            domain (str): Domain name for the Virtual Host
            port (int): Local port to proxy to
            use_ssl (bool): Whether to configure SSL/HTTPS
            
        Returns:
            str: Path to created configuration file, None if failed
        """
        logger.info(f"Creating Virtual Host configuration for {domain}:{port}")
        
        # Configuration for HTTP (with or without SSL redirect)
        if use_ssl:
            http_config = f"""<VirtualHost *:80>
    ServerName {domain}
    ServerAlias www.{domain}
    
    # Force HTTPS redirect
    RewriteEngine On
    RewriteCond %{{HTTPS}} off
    RewriteRule ^(.*)$ https://%{{HTTP_HOST}}%{{REQUEST_URI}} [R=301,L]
    
    # Logging
    ErrorLog ${{APACHE_LOG_DIR}}/{domain}-error.log
    CustomLog ${{APACHE_LOG_DIR}}/{domain}-access.log combined
    
    # Security headers even for redirects
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
</VirtualHost>"""
        else:
            http_config = f"""<VirtualHost *:80>
    ServerName {domain}
    ServerAlias www.{domain}
    
    # Logging
    ErrorLog ${{APACHE_LOG_DIR}}/{domain}-error.log
    CustomLog ${{APACHE_LOG_DIR}}/{domain}-access.log combined
    
    # Proxy configuration
    ProxyPreserveHost On
    ProxyPass / http://localhost:{port}/
    ProxyPassReverse / http://localhost:{port}/
    
    # Proxy headers
    ProxyAddHeaders On
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-For %{{REMOTE_ADDR}}s
    RequestHeader set X-Real-IP %{{REMOTE_ADDR}}s
    
    # Security headers
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
</VirtualHost>"""

        # HTTPS configuration
        https_config = f"""
# HTTPS Configuration
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName {domain}
    ServerAlias www.{domain}
    
    # Logging
    ErrorLog ${{APACHE_LOG_DIR}}/{domain}-ssl-error.log
    CustomLog ${{APACHE_LOG_DIR}}/{domain}-ssl-access.log combined
    
    # Proxy configuration
    ProxyPreserveHost On
    ProxyPass / http://localhost:{port}/
    ProxyPassReverse / http://localhost:{port}/
    
    # Proxy headers for HTTPS
    ProxyAddHeaders On
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-For %{{REMOTE_ADDR}}s
    RequestHeader set X-Real-IP %{{REMOTE_ADDR}}s
    
    # SSL Configuration (will be managed by Certbot)
    SSLEngine on
    # Default certificates (will be replaced by Certbot)
    SSLCertificateFile /etc/ssl/certs/ssl-cert-snakeoil.pem
    SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key
    
    # Modern SSL configuration
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    SSLHonorCipherOrder off
    SSLSessionTickets off
    
    # Security headers for HTTPS
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
</VirtualHost>
</IfModule>"""
        
        # Combine configurations
        config_content = http_config + https_config
        config_path = f"{self.sites_available}/{domain}.conf"
        
        try:
            # Ensure sites-available directory exists
            os.makedirs(self.sites_available, exist_ok=True)
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            # Set appropriate permissions
            os.chmod(config_path, 0o644)
            
            logger.info(f"Virtual Host configuration created: {config_path}")
            return config_path
            
        except Exception as e:
            logger.error(f"Failed to create configuration file: {e}")
            print(f"❌ Error creating configuration file: {e}")
            return None
    
    def enable_modules(self):
        """Enable required Apache modules"""
        modules = ['proxy', 'proxy_http', 'rewrite', 'ssl', 'headers']
        print("🔧 Enabling required Apache modules...")
        
        for module in modules:
            if self.run_command(f"a2enmod {module}"):
                logger.info(f"Enabled Apache module: {module}")
            else:
                logger.warning(f"Failed to enable module {module} (may already be enabled)")
    
    def validate_domain(self, domain):
        """
        Validate domain name format
        
        Args:
            domain (str): Domain name to validate
            
        Returns:
            bool: True if domain is valid, False otherwise
        """
        # Basic domain validation regex
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        
        if not re.match(domain_pattern, domain):
            return False
        
        # Additional checks
        if len(domain) > 253:
            return False
        
        if domain.startswith('-') or domain.endswith('-'):
            return False
        
        return True
    
    def validate_port(self, port):
        """
        Validate port number
        
        Args:
            port (str or int): Port number to validate
            
        Returns:
            int: Valid port number, None if invalid
        """
        try:
            port_num = int(port)
            if 1 <= port_num <= 65535:
                return port_num
            else:
                print(f"❌ Port {port_num} is out of valid range (1-65535)")
                return None
        except ValueError:
            print(f"❌ Invalid port format: {port}")
            return None
    
    def check_port_in_use(self, port):
        """
        Check if a port is currently in use on localhost
        
        Args:
            port (int): Port number to check
            
        Returns:
            bool: True if port is in use (service running), False if available
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # connect_ex returns 0 if connection succeeds (port in use)
                # returns non-zero if connection fails (port available)
                result = s.connect_ex(('localhost', port))
                return result == 0  # Port is in use if connection succeeds
        except Exception:
            return False  # Assume available if check fails
    
    def check_domain_dns(self, domain):
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
    
    def get_validated_email(self):
        """
        Get and validate email for Let's Encrypt
        
        Returns:
            str: Validated email address
        """
        email_file = "/etc/letsencrypt/.email"
        
        # Check if email already saved
        if os.path.exists(email_file):
            try:
                with open(email_file, 'r') as f:
                    saved_email = f.read().strip()
                    # Validate saved email
                    valid = validate_email(saved_email)
                    return valid.email
            except Exception as e:
                logger.warning(f"Saved email is invalid: {e}")
                # Continue to ask for new email
        
        # Get new email with validation
        print("📧 Let's Encrypt requires a valid email for:")
        print("   • Certificate expiration notifications")
        print("   • Security alerts")
        print("   • Important updates")
        print()
        
        while True:
            email = input("Enter your email: ").strip()
            
            try:
                # Validate and normalize email
                valid = validate_email(email)
                normalized_email = valid.email
                
                # Save for future use
                os.makedirs(os.path.dirname(email_file), exist_ok=True)
                with open(email_file, 'w') as f:
                    f.write(normalized_email)
                os.chmod(email_file, 0o644)
                
                logger.info(f"Email validated and saved: {normalized_email}")
                return normalized_email
                
            except EmailNotValidError as e:
                print(f"❌ Invalid email: {e}")
                print("💡 Example: user@example.com")
                print()
    
    def install_ssl_certificate(self, domain):
        """
        Install SSL certificate using Let's Encrypt
        
        Args:
            domain (str): Domain name for SSL certificate
            
        Returns:
            bool: True if certificate was installed successfully
        """
        print(f"🔒 Installing SSL certificate for {domain}...")
        
        # Check if certbot is installed
        if not self.run_command("which certbot"):
            print("📦 Certbot not found. Installing Certbot...")
            if not self.run_command("apt update && apt install -y certbot python3-certbot-apache"):
                print("❌ Failed to install Certbot")
                return False
        
        # Check if domain DNS points to current server
        print("🔍 Checking domain DNS configuration...")
        if not self.check_domain_dns(domain):
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
            self.run_command(f"a2dissite {domain}.conf", show_output=False)
            self.run_command(f"a2ensite {domain}-temp.conf")
            self.run_command("systemctl reload apache2")
            
        except Exception as e:
            print(f"❌ Failed to create temporary configuration: {e}")
            return False
        
        # Get SSL certificate
        certbot_cmd = f"certbot --apache -d {domain} -d www.{domain} --non-interactive --agree-tos"
        
        # Get validated email
        email = self.get_validated_email()
        certbot_cmd += f" --email {email}"
        
        # Run certbot
        success = self.run_command(certbot_cmd, show_output=True)
        
        # Clean up temporary configuration
        self.run_command(f"a2dissite {domain}-temp.conf", show_output=False)
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
    
    def create_site(self, domain, port, ssl=True):
        """
        Create a new Virtual Host
        
        Args:
            domain (str): Domain name
            port (int): Local port to proxy to
            ssl (bool): Whether to install SSL certificate
        """
        self.check_sudo()
        
        # Validate inputs
        if not self.validate_domain(domain):
            print(f"❌ Invalid domain name: {domain}")
            return
        
        port_num = self.validate_port(port)
        if port_num is None:
            return
        
        # Check if site already exists
        if domain in self.sites:
            response = input(f"⚠️  Site {domain} already exists. Replace it? (y/n): ")
            if response.lower() != 'y':
                return
        
        # Check if port is in use
        if self.check_port_in_use(port_num):
            print(f"💡 Service appears to be running on port {port_num}")
        else:
            print(f"⚠️  Warning: No service detected on port {port_num}")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return
        
        print(f"🚀 Creating Virtual Host for {domain} on port {port_num}...")
        
        # Create configuration file
        config_path = self.create_vhost_config(domain, port_num, ssl)
        if not config_path:
            return
        
        # Enable required modules
        self.enable_modules()
        
        # Enable the site
        if not self.run_command(f"a2ensite {domain}"):
            print(f"❌ Failed to enable site {domain}")
            return
        
        # Test Apache configuration
        if not self.run_command("apache2ctl configtest"):
            print("❌ Invalid Apache configuration")
            self.run_command("apache2ctl configtest", show_output=True)
            return
        
        # Reload Apache
        if self.run_command("systemctl reload apache2"):
            print("✅ Basic configuration created!")
            
            # Install SSL certificate if requested
            ssl_success = True
            if ssl:
                response = input("🔒 Install SSL certificate with Let's Encrypt? (y/n): ")
                if response.lower() == 'y':
                    ssl_success = self.install_ssl_certificate(domain)
                    
                    # If SSL was successful, recreate the virtual host with proper SSL configuration
                    if ssl_success:
                        print("🔧 Updating virtual host configuration with SSL...")
                        # Disable current site
                        self.run_command(f"a2dissite {domain}.conf", show_output=False)
                        
                        # Recreate config with SSL enabled
                        new_config_path = self.create_vhost_config(domain, port_num, True)
                        if new_config_path:
                            # Enable the updated site
                            self.run_command(f"a2ensite {domain}")
                            self.run_command("systemctl reload apache2")
                            print("✅ SSL configuration updated!")
                        else:
                            print("⚠️  Warning: Failed to update SSL configuration")
                else:
                    ssl = False
            # Save configuration
            self.sites[domain] = {
                'port': port_num,
                'ssl': ssl and ssl_success,
                'created': datetime.now().isoformat(),
                'config_file': config_path
            }
            self.save_config()
            
            print("\n✅ Virtual Host created successfully!")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📍 Domain: {domain}")
            print(f"🔌 Port: {port_num}")
            if ssl and ssl_success:
                print(f"🔒 HTTPS: Enabled (automatic redirect)")
                print(f"🌐 URL: https://{domain}")
            else:
                print(f"🌐 URL: http://{domain}")
            print(f"📁 Config: {config_path}")
            print(f"📝 Logs: /var/log/apache2/{domain}-*.log")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        else:
            print("❌ Failed to reload Apache")
    
    def delete_site(self, domain):
        """
        Delete a Virtual Host
        
        Args:
            domain (str): Domain name to delete
        """
        self.check_sudo()
        
        if domain not in self.sites:
            print(f"❌ Site {domain} does not exist in configuration")
            return
        
        print(f"🗑️  Deleting Virtual Host {domain}...")
        
        # Disable the site 
        self.run_command(f"a2dissite {domain}.conf")
        
        # Remove configuration file
        config_file = self.sites[domain]['config_file']
        if os.path.exists(config_file):
            os.remove(config_file)
            logger.info(f"Removed configuration file: {config_file}")
        
        # Reload Apache
        if self.run_command("systemctl reload apache2"):
            del self.sites[domain]
            self.save_config()
            print(f"✅ Site {domain} deleted successfully")
            logger.info(f"Deleted Virtual Host: {domain}")
        else:
            print("❌ Failed to reload Apache")
    
    def list_sites(self):
        """List all configured sites"""
        if not self.sites:
            print("📝 No sites configured")
            return
        
        print("📋 Configured Sites:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for domain, config in self.sites.items():
            ssl_status = "🔒 HTTPS" if config.get('ssl', False) else "🔓 HTTP"
            created_date = datetime.fromisoformat(config['created']).strftime('%Y-%m-%d %H:%M')
            
            print(f"🌐 {domain} - {ssl_status}")
            print(f"   Port: {config['port']}")
            print(f"   Created: {created_date}")
            print(f"   Config: {config['config_file']}")
            print()
    
    def renew_ssl_certificates(self):
        """Renew all SSL certificates"""
        self.check_sudo()
        print("🔄 Renewing SSL certificates...")
        
        if self.run_command("certbot renew --quiet"):
            print("✅ SSL certificates renewed")
            self.run_command("systemctl reload apache2")
            logger.info("SSL certificates renewed successfully")
        else:
            print("❌ Failed to renew SSL certificates")
            logger.error("SSL certificate renewal failed")
    
    def show_version(self):
        """Show version information"""
        print(f"Apache Virtual Host Manager v{self.VERSION}")
        print("Repository: https://github.com/Noubissie237/reverse-proxy")
        print("Author: Noubissie237")
    
    def check_site_status(self, domain):
        """
        Check the status of a specific site
        
        Args:
            domain (str): Domain name to check
            
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
        
        if domain not in self.sites:
            return status
        
        site_config = self.sites[domain]
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
        status['port_active'] = self.check_port_in_use(port)
        
        # Check SSL status
        status['ssl_enabled'] = site_config.get('ssl', False)
        
        if status['ssl_enabled']:
            ssl_info = self.get_ssl_certificate_info(domain)
            if ssl_info:
                status['ssl_valid'] = ssl_info['valid']
                status['ssl_days_remaining'] = ssl_info['days_remaining']
        
        return status
    
    def get_ssl_certificate_info(self, domain):
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
    
    def show_status(self):
        """Show detailed status of all sites"""
        if not self.sites:
            print("📝 No sites configured")
            return
        
        print("\n" + "=" * 80)
        print("📊 SITES STATUS REPORT")
        print("=" * 80 + "\n")
        
        for domain in sorted(self.sites.keys()):
            status = self.check_site_status(domain)
            site_config = self.sites[domain]
            
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
                        ssl_color = ""
                    elif days > 7:
                        ssl_icon = "⚠️ "
                        ssl_color = ""
                    else:
                        ssl_icon = "🔴"
                        ssl_color = ""
                    
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
    
    def check_ssl_certificates(self):
        """Check all SSL certificates and show expiration info"""
        ssl_sites = {domain: config for domain, config in self.sites.items() 
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
            ssl_info = self.get_ssl_certificate_info(domain)
            
            if ssl_info is None:
                print(f"❌ {domain:40} Certificate not found")
                errors.append(domain)
                continue
            
            days = ssl_info['days_remaining']
            expiry = ssl_info['expiry_date'].strftime('%Y-%m-%d %H:%M')
            
            if days > 30:
                icon = "✅"
                status = "Valid"
            elif days > 7:
                icon = "⚠️ "
                status = "Expiring soon"
                warnings.append((domain, days))
            elif days > 0:
                icon = "🔴"
                status = "CRITICAL - Expiring very soon"
                warnings.append((domain, days))
            else:
                icon = "❌"
                status = "EXPIRED"
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
            print(f"\n💡 Run: sudo python3 vhost_manager.py renew-ssl")
        
        if errors:
            print(f"\n❌ Critical issues with {len(errors)} certificate(s):")
            for domain in errors:
                print(f"  - {domain}")
        
        print()
    
    def show_stats(self):
        """Show statistics about configured sites"""
        if not self.sites:
            print("📝 No sites configured")
            return
        
        total_sites = len(self.sites)
        ssl_sites = sum(1 for config in self.sites.values() if config.get('ssl', False))
        non_ssl_sites = total_sites - ssl_sites
        
        # Count active sites
        active_sites = 0
        for domain in self.sites.keys():
            status = self.check_site_status(domain)
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
        for config in self.sites.values():
            port = config['port']
            ports[port] = ports.get(port, 0) + 1
        
        print(f"🔌 Port Distribution:")
        for port, count in sorted(ports.items()):
            print(f"   Port {port:5}: {count} site(s)")
        
        print("\n" + "=" * 80 + "\n")

def main():
    """Main function to handle command line arguments"""
    manager = ApacheVHostManager()
    
    if len(sys.argv) < 2:
        print("Apache Virtual Host Manager")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Usage:")
        print("  sudo python3 vhost_manager.py create <domain> <port> [--no-ssl]")
        print("  sudo python3 vhost_manager.py delete <domain>")
        print("  python3 vhost_manager.py list")
        print("  python3 vhost_manager.py status")
        print("  python3 vhost_manager.py check-ssl")
        print("  python3 vhost_manager.py stats")
        print("  sudo python3 vhost_manager.py renew-ssl")
        print("  python3 vhost_manager.py version")
        print()
        print("Examples:")
        print("  sudo python3 vhost_manager.py create mysite.com 8080")
        print("  sudo python3 vhost_manager.py create api.example.com 3000 --no-ssl")
        print("  sudo python3 vhost_manager.py delete mysite.com")
        print("  python3 vhost_manager.py list")
        print("  python3 vhost_manager.py status")
        print("  python3 vhost_manager.py check-ssl")
        sys.exit(1)
    
    action = sys.argv[1]
    
    try:
        if action == "create":
            if len(sys.argv) < 4:
                print("Usage: sudo python3 vhost_manager.py create <domain> <port> [--no-ssl]")
                sys.exit(1)
            domain = sys.argv[2]
            port = sys.argv[3]
            ssl = "--no-ssl" not in sys.argv
            manager.create_site(domain, port, ssl)
        
        elif action == "delete":
            if len(sys.argv) != 3:
                print("Usage: sudo python3 vhost_manager.py delete <domain>")
                sys.exit(1)
            domain = sys.argv[2]
            manager.delete_site(domain)
        
        elif action == "list":
            manager.list_sites()
        
        elif action == "status":
            manager.show_status()
        
        elif action == "check-ssl":
            manager.check_ssl_certificates()
        
        elif action == "stats":
            manager.show_stats()
        
        elif action == "renew-ssl":
            manager.renew_ssl_certificates()
        
        elif action == "version":
            manager.show_version()
        
        else:
            print(f"Unknown action: {action}")
            print("Available actions: create, delete, list, status, check-ssl, stats, renew-ssl, version")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ An unexpected error occurred: {e}")
        print("Please check the logs for more details: /var/log/vhost-manager/manager.log")
        sys.exit(1)

if __name__ == "__main__":
    main()