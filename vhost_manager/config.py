"""
Configuration management for Virtual Hosts
"""
import json
import os
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manage Virtual Host configuration"""
    
    def __init__(self, config_file="/etc/vhost_manager.json"):
        self.config_file = config_file
        self.sites = {}
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
        """Save site configurations to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.sites, f, indent=2)
            logger.info(f"Configuration saved with {len(self.sites)} sites")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def add_site(self, domain, port, ssl, config_file, created):
        """Add a site to configuration"""
        self.sites[domain] = {
            'port': port,
            'ssl': ssl,
            'created': created,
            'config_file': config_file
        }
        self.save_config()
    
    def remove_site(self, domain):
        """Remove a site from configuration"""
        if domain in self.sites:
            del self.sites[domain]
            self.save_config()
            return True
        return False
    
    def get_site(self, domain):
        """Get site configuration"""
        return self.sites.get(domain)
    
    def list_sites(self):
        """List all configured sites"""
        return self.sites
    
    def site_exists(self, domain):
        """Check if site exists"""
        return domain in self.sites
