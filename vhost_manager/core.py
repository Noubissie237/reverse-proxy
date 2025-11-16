"""
Core functionality for Apache Virtual Host management
"""
import os
import logging
from datetime import datetime
from .config import ConfigManager
from .validation import (
    validate_domain, validate_port, is_wildcard_domain,
    validate_wildcard_domain
)
from .ssl import install_ssl_certificate, install_wildcard_ssl_certificate
from .monitoring import check_port_in_use
from .utils import check_sudo, run_command

logger = logging.getLogger(__name__)


class ApacheVHostManager:
    """Apache Virtual Host Manager"""
    
    VERSION = "1.5.0"
    
    def __init__(self):
        self.sites_available = "/etc/apache2/sites-available"
        self.log_dir = "/var/log/vhost-manager"
        
        # Ensure log directory exists (with fallback for non-root)
        try:
            os.makedirs(self.log_dir, exist_ok=True)
        except PermissionError:
            self.log_dir = os.path.expanduser("~/.vhost-manager/logs")
            os.makedirs(self.log_dir, exist_ok=True)
        
        # Load configuration
        self.config_manager = ConfigManager()
        self.sites = self.config_manager.sites
    
    def enable_modules(self):
        """Enable required Apache modules"""
        modules = ['proxy', 'proxy_http', 'rewrite', 'ssl', 'headers']
        print("🔧 Enabling required Apache modules...")
        
        for module in modules:
            if run_command(f"a2enmod {module}"):
                logger.info(f"Enabled Apache module: {module}")
            else:
                logger.warning(f"Failed to enable module {module} (may already be enabled)")
    
    def create_vhost_config(self, domain, port, ssl=False):
        """
        Create Apache Virtual Host configuration file
        
        Args:
            domain (str): Domain name
            port (int): Local port to proxy to
            ssl (bool): Whether SSL is configured
            
        Returns:
            str: Path to configuration file, or None if failed
        """
        config_path = f"{self.sites_available}/{domain}.conf"
        
        # Determine certificate path (handle wildcards)
        if is_wildcard_domain(domain):
            from .validation import get_base_domain
            cert_domain = get_base_domain(domain)
        else:
            cert_domain = domain
        
        if ssl:
            config = f"""<VirtualHost *:80>
    ServerName {domain}
    ServerAlias www.{domain}
    
    # Redirect all HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{{HTTPS}} off
    RewriteRule ^(.*)$ https://%{{HTTP_HOST}}$1 [R=301,L]
</VirtualHost>

<VirtualHost *:443>
    ServerName {domain}
    ServerAlias www.{domain}
    
    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/{cert_domain}/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/{cert_domain}/privkey.pem
    
    # Security Headers
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    
    # Proxy Configuration
    ProxyPreserveHost On
    ProxyPass / http://localhost:{port}/
    ProxyPassReverse / http://localhost:{port}/
    
    # Logging
    ErrorLog ${{APACHE_LOG_DIR}}/{domain}-error.log
    CustomLog ${{APACHE_LOG_DIR}}/{domain}-access.log combined
</VirtualHost>"""
        else:
            config = f"""<VirtualHost *:80>
    ServerName {domain}
    ServerAlias www.{domain}
    
    # Proxy Configuration
    ProxyPreserveHost On
    ProxyPass / http://localhost:{port}/
    ProxyPassReverse / http://localhost:{port}/
    
    # Logging
    ErrorLog ${{APACHE_LOG_DIR}}/{domain}-error.log
    CustomLog ${{APACHE_LOG_DIR}}/{domain}-access.log combined
</VirtualHost>"""
        
        try:
            with open(config_path, 'w') as f:
                f.write(config)
            logger.info(f"Created configuration file: {config_path}")
            return config_path
        except Exception as e:
            logger.error(f"Failed to create configuration file: {e}")
            print(f"❌ Failed to create configuration file: {e}")
            return None
    
    def create_site(self, domain, port, ssl=True, interactive=True, force=False):
        """
        Create a new Virtual Host
        
        Args:
            domain (str): Domain name
            port (int): Local port to proxy to
            ssl (bool): Whether to install SSL certificate
            interactive (bool): Whether to prompt for user input (default: True)
            force (bool): Force creation without prompts (default: False)
            
        Returns:
            dict: {'success': bool, 'message': str, 'error': str or None}
        """
        check_sudo()
        
        errors = []  # Collect errors for web interface
        
        # Check if wildcard domain
        is_wildcard = is_wildcard_domain(domain)
        
        # Validate inputs
        if is_wildcard:
            if not validate_wildcard_domain(domain):
                error_msg = f"Invalid wildcard domain name: {domain}"
                print(f"❌ {error_msg}")
                return {'success': False, 'message': error_msg, 'error': error_msg}
            print(f"🌟 Wildcard domain detected: {domain}")
        else:
            if not validate_domain(domain):
                error_msg = f"Invalid domain name: {domain}"
                print(f"❌ {error_msg}")
                return {'success': False, 'message': error_msg, 'error': error_msg}
        
        port_num = validate_port(port)
        if port_num is None:
            error_msg = f"Invalid port: {port}"
            return {'success': False, 'message': error_msg, 'error': error_msg}
        
        # Check if site already exists
        if domain in self.sites:
            if interactive and not force:
                response = input(f"⚠️  Site {domain} already exists. Replace it? (y/n): ")
                if response.lower() != 'y':
                    return {'success': False, 'message': 'Operation cancelled', 'error': None}
            elif not force:
                error_msg = f"Site {domain} already exists"
                print(f"❌ {error_msg}")
                return {'success': False, 'message': error_msg, 'error': error_msg}
        
        # Check if port is in use
        if check_port_in_use(port_num):
            print(f"💡 Service appears to be running on port {port_num}")
        else:
            print(f"⚠️  Warning: No service detected on port {port_num}")
            if interactive and not force:
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    return
            elif not force:
                print("⚠️  Continuing anyway (non-interactive mode)...")
        
        print(f"🚀 Creating Virtual Host for {domain} on port {port_num}...")
        
        # Create configuration file
        config_path = self.create_vhost_config(domain, port_num, ssl=False)
        if not config_path:
            error_msg = f"Failed to create configuration file for {domain}"
            errors.append(error_msg)
            return {'success': False, 'message': error_msg, 'error': '\n'.join(errors)}
        
        # Enable required modules
        self.enable_modules()
        
        # Enable the site
        if not run_command(f"a2ensite {domain}"):
            error_msg = f"Failed to enable site {domain}. Check if Apache Agent is running: sudo systemctl status apache-agent"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
            return {'success': False, 'message': error_msg, 'error': '\n'.join(errors)}
        
        # Test Apache configuration
        if not run_command("apache2ctl configtest"):
            error_msg = "Invalid Apache configuration"
            print(f"❌ {error_msg}")
            run_command("apache2ctl configtest", show_output=True)
            errors.append(error_msg)
            return {'success': False, 'message': error_msg, 'error': '\n'.join(errors)}
        
        # Reload Apache
        if run_command("systemctl reload apache2"):
            print("✅ Basic configuration created!")
            
            # Install SSL certificate if requested
            ssl_success = True
            if ssl:
                # In interactive mode, ask for confirmation
                install_ssl_cert = True
                if interactive:
                    response = input("🔒 Install SSL certificate with Let's Encrypt? (y/n): ")
                    install_ssl_cert = response.lower() == 'y'
                
                if install_ssl_cert:
                    # Use wildcard SSL if domain is wildcard
                    if is_wildcard:
                        ssl_success = install_wildcard_ssl_certificate(domain)
                    else:
                        ssl_success = install_ssl_certificate(domain)
                    
                    # If SSL was successful, recreate the virtual host with proper SSL configuration
                    if ssl_success:
                        print("🔧 Updating virtual host configuration with SSL...")
                        # Disable current site
                        run_command(f"a2dissite {domain}.conf", show_output=False)
                        
                        # Recreate config with SSL enabled
                        new_config_path = self.create_vhost_config(domain, port_num, True)
                        if new_config_path:
                            # Enable the updated site
                            run_command(f"a2ensite {domain}")
                            run_command("systemctl reload apache2")
                            print("✅ SSL configuration updated!")
                        else:
                            print("⚠️  Warning: Failed to update SSL configuration")
                else:
                    ssl = False
            
            # Save configuration
            self.config_manager.add_site(
                domain=domain,
                port=port_num,
                ssl=ssl and ssl_success,
                config_file=config_path,
                created=datetime.now().isoformat()
            )
            
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
            
            return {'success': True, 'message': f'Site {domain} created successfully!', 'error': None}
        else:
            error_msg = "Failed to reload Apache"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
            return {'success': False, 'message': error_msg, 'error': '\n'.join(errors)}
    
    def delete_site(self, domain):
        """
        Delete a Virtual Host
        
        Args:
            domain (str): Domain name to delete
        """
        check_sudo()
        
        if domain not in self.sites:
            print(f"❌ Site {domain} does not exist in configuration")
            return
        
        print(f"🗑️  Deleting Virtual Host {domain}...")
        
        # Disable the site
        run_command(f"a2dissite {domain}.conf")
        
        # Remove configuration file
        config_file = self.sites[domain]['config_file']
        if os.path.exists(config_file):
            os.remove(config_file)
            logger.info(f"Removed configuration file: {config_file}")
        
        # Reload Apache
        if run_command("systemctl reload apache2"):
            self.config_manager.remove_site(domain)
            print(f"✅ Site {domain} deleted successfully")
            logger.info(f"Deleted Virtual Host: {domain}")
        else:
            print("❌ Failed to reload Apache")
    
    def list_sites(self):
        """List all configured Virtual Hosts"""
        if not self.sites:
            print("📝 No sites configured")
            return
        
        print("📋 Configured Sites:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        for domain, config in sorted(self.sites.items()):
            ssl_status = "🔒 HTTPS" if config.get('ssl', False) else "🔓 HTTP"
            created = datetime.fromisoformat(config['created']).strftime('%Y-%m-%d %H:%M')
            
            print(f"🌐 {domain} - {ssl_status}")
            print(f"   Port: {config['port']}")
            print(f"   Created: {created}")
            print(f"   Config: {config['config_file']}")
            print()
    
    def show_version(self):
        """Show version information"""
        print(f"Apache Virtual Host Manager v{self.VERSION}")
        print("Repository: https://github.com/Noubissie237/reverse-proxy")
        print("Author: Noubissie237")
