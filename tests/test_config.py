"""
Tests for configuration management
"""
import pytest
import json
import tempfile
import os
from datetime import datetime


class TestConfigManagement:
    """Test configuration loading and saving"""
    
    def test_load_empty_config(self, mock_manager):
        """Test loading when no config file exists"""
        mock_manager.config_file = "/nonexistent/path/config.json"
        mock_manager.load_config()
        assert mock_manager.sites == {}
    
    def test_save_and_load_config(self, mock_manager, sample_site_config):
        """Test saving and loading configuration"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            mock_manager.config_file = temp_file
            mock_manager.sites = {
                'example.com': sample_site_config
            }
            
            # Save
            mock_manager.save_config()
            assert os.path.exists(temp_file)
            
            # Load
            mock_manager.sites = {}
            mock_manager.load_config()
            assert 'example.com' in mock_manager.sites
            assert mock_manager.sites['example.com']['port'] == 8080
            assert mock_manager.sites['example.com']['ssl'] is True
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_config_json_format(self, mock_manager, sample_site_config):
        """Test that saved config is valid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            mock_manager.config_file = temp_file
            mock_manager.sites = {
                'example.com': sample_site_config,
                'api.example.com': {
                    'port': 3000,
                    'ssl': False,
                    'created': datetime.now().isoformat(),
                    'config_file': '/etc/apache2/sites-available/api.example.com.conf'
                }
            }
            
            mock_manager.save_config()
            
            # Read and verify JSON
            with open(temp_file, 'r') as f:
                data = json.load(f)
            
            assert isinstance(data, dict)
            assert len(data) == 2
            assert 'example.com' in data
            assert 'api.example.com' in data
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_multiple_sites(self, mock_manager):
        """Test managing multiple sites"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            mock_manager.config_file = temp_file
            
            # Add multiple sites
            sites = {
                f'site{i}.example.com': {
                    'port': 8000 + i,
                    'ssl': i % 2 == 0,
                    'created': datetime.now().isoformat(),
                    'config_file': f'/etc/apache2/sites-available/site{i}.example.com.conf'
                }
                for i in range(5)
            }
            
            mock_manager.sites = sites
            mock_manager.save_config()
            
            # Load and verify
            mock_manager.sites = {}
            mock_manager.load_config()
            
            assert len(mock_manager.sites) == 5
            assert mock_manager.sites['site0.example.com']['ssl'] is True
            assert mock_manager.sites['site1.example.com']['ssl'] is False
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestSiteOperations:
    """Test site-related operations"""
    
    def test_site_exists_check(self, mock_manager, sample_site_config):
        """Test checking if a site exists"""
        mock_manager.sites = {'example.com': sample_site_config}
        
        assert 'example.com' in mock_manager.sites
        assert 'nonexistent.com' not in mock_manager.sites
    
    def test_get_site_config(self, mock_manager, sample_site_config):
        """Test retrieving site configuration"""
        mock_manager.sites = {'example.com': sample_site_config}
        
        config = mock_manager.sites.get('example.com')
        assert config is not None
        assert config['port'] == 8080
        assert config['ssl'] is True
    
    def test_site_count(self, mock_manager):
        """Test counting sites"""
        mock_manager.sites = {
            'site1.com': {'port': 8080, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site2.com': {'port': 3000, 'ssl': False, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site3.com': {'port': 8000, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
        }
        
        assert len(mock_manager.sites) == 3
        
        # Count SSL sites
        ssl_count = sum(1 for config in mock_manager.sites.values() if config.get('ssl', False))
        assert ssl_count == 2
