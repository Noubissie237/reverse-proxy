#!/usr/bin/env python3

import sys
import os
import subprocess
import json
import logging
import socket
import re
from pathlib import Path
from datetime import datetime

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    log_dir = "/var/log/vhost-manager"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{log_dir}/manager.log'),
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
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.sites_available = "/etc/apache2/sites-available"
        self.config_file = "/etc/vhost_manager.json"
        self.log_dir = "/var/log/vhost-manager"
        
        # Ensure log directory exists
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
    
    def check_port_available(self, port):
        """
        Check if a port is available on localhost
        
        Args:
            port (int): Port number to check
            
        Returns:
            bool: True if port is available, False if in use
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('localhost', port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return True  # Assume available if check fails
    
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
        
        # Get SSL certificate
        certbot_cmd = f"certbot --apache -d {domain} -d www.{domain} --non-interactive --agree-tos --redirect"
        
        # Handle email configuration
        email_file = "/etc/letsencrypt/.email"
        if not os.path.exists(email_file):
            email = input("📧 Enter your email for Let's Encrypt notifications: ")
            certbot_cmd += f" --email {email}"
            # Save email for future use
            os.makedirs(os.path.dirname(email_file), exist_ok=True)
            with open(email_file, 'w') as f:
                f.write(email)
        else:
            with open(email_file, 'r') as f:
                email = f.read().strip()
            certbot_cmd += f" --email {email}"
        
        if self.run_command(certbot_cmd, show_output=True):
            print("✅ SSL certificate installed successfully!")
            print("🔄 Automatic renewal is configured")
            logger.info(f"SSL certificate installed for {domain}")
            return True
        else:
            print("❌ Failed to install SSL certificate")
            print("💡 Make sure your DNS points to this server and port 80/443 are accessible")
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
        
        # Warn if port is not responding
        if not self.check_port_available(port_num):
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
        self.run_command(f"a2dissite {domain}")
        
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
        print("  sudo python3 vhost_manager.py renew-ssl")
        print("  python3 vhost_manager.py version")
        print()
        print("Examples:")
        print("  sudo python3 vhost_manager.py create mysite.com 8080")
        print("  sudo python3 vhost_manager.py create api.example.com 3000 --no-ssl")
        print("  sudo python3 vhost_manager.py delete mysite.com")
        print("  python3 vhost_manager.py list")
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
        
        elif action == "renew-ssl":
            manager.renew_ssl_certificates()
        
        elif action == "version":
            manager.show_version()
        
        else:
            print(f"Unknown action: {action}")
            print("Available actions: create, delete, list, renew-ssl, version")
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