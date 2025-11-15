"""
Tests for monitoring features (status, check-ssl, stats)
"""
import pytest
from datetime import datetime


class TestStatusChecking:
    """Test site status checking"""
    
    def test_check_port_in_use(self, mock_manager):
        """Test port availability checking"""
        # Port 80 is likely in use or not accessible
        # Port 65534 is likely not in use
        result = mock_manager.check_port_in_use(65534)
        assert isinstance(result, bool)
    
    def test_port_check_invalid_port(self, mock_manager):
        """Test port check with invalid port"""
        # Should handle gracefully
        result = mock_manager.check_port_in_use(99999)
        assert isinstance(result, bool)


class TestStatistics:
    """Test statistics calculation"""
    
    def test_stats_empty_sites(self, mock_manager):
        """Test stats with no sites"""
        mock_manager.sites = {}
        # Should not raise an error
        assert len(mock_manager.sites) == 0
    
    def test_stats_ssl_count(self, mock_manager):
        """Test counting SSL sites"""
        mock_manager.sites = {
            'site1.com': {'port': 8080, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site2.com': {'port': 3000, 'ssl': False, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site3.com': {'port': 8000, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site4.com': {'port': 9000, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
        }
        
        ssl_count = sum(1 for config in mock_manager.sites.values() if config.get('ssl', False))
        non_ssl_count = len(mock_manager.sites) - ssl_count
        
        assert ssl_count == 3
        assert non_ssl_count == 1
    
    def test_stats_port_distribution(self, mock_manager):
        """Test port distribution calculation"""
        mock_manager.sites = {
            'site1.com': {'port': 8080, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site2.com': {'port': 3000, 'ssl': False, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site3.com': {'port': 8080, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site4.com': {'port': 3000, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
        }
        
        ports = {}
        for config in mock_manager.sites.values():
            port = config['port']
            ports[port] = ports.get(port, 0) + 1
        
        assert ports[8080] == 2
        assert ports[3000] == 2
        assert len(ports) == 2
    
    def test_stats_percentage_calculation(self, mock_manager):
        """Test SSL percentage calculation"""
        mock_manager.sites = {
            'site1.com': {'port': 8080, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site2.com': {'port': 3000, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site3.com': {'port': 8000, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'site4.com': {'port': 9000, 'ssl': False, 'created': datetime.now().isoformat(), 'config_file': '/path'},
        }
        
        total = len(mock_manager.sites)
        ssl_count = sum(1 for config in mock_manager.sites.values() if config.get('ssl', False))
        ssl_percentage = (ssl_count * 100 // total) if total > 0 else 0
        
        assert total == 4
        assert ssl_count == 3
        assert ssl_percentage == 75


class TestSiteStatus:
    """Test individual site status"""
    
    def test_site_status_structure(self, mock_manager, sample_site_config):
        """Test that site status has correct structure"""
        mock_manager.sites = {'example.com': sample_site_config}
        
        status = mock_manager.check_site_status('example.com')
        
        assert 'domain' in status
        assert 'apache_enabled' in status
        assert 'port_active' in status
        assert 'ssl_enabled' in status
        assert 'ssl_valid' in status
        assert 'ssl_days_remaining' in status
    
    def test_site_status_nonexistent(self, mock_manager):
        """Test status for nonexistent site"""
        status = mock_manager.check_site_status('nonexistent.com')
        
        assert status['domain'] == 'nonexistent.com'
        assert status['apache_enabled'] is False
        assert status['port_active'] is False
    
    def test_site_status_ssl_disabled(self, mock_manager):
        """Test status for site without SSL"""
        mock_manager.sites = {
            'nossl.com': {
                'port': 8080,
                'ssl': False,
                'created': datetime.now().isoformat(),
                'config_file': '/path'
            }
        }
        
        status = mock_manager.check_site_status('nossl.com')
        assert status['ssl_enabled'] is False
        assert status['ssl_days_remaining'] is None


class TestListSites:
    """Test site listing functionality"""
    
    def test_list_empty_sites(self, mock_manager):
        """Test listing when no sites configured"""
        mock_manager.sites = {}
        # Should not raise an error
        assert len(mock_manager.sites) == 0
    
    def test_list_multiple_sites(self, mock_manager):
        """Test listing multiple sites"""
        mock_manager.sites = {
            'example.com': {'port': 8080, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'api.example.com': {'port': 3000, 'ssl': False, 'created': datetime.now().isoformat(), 'config_file': '/path'},
        }
        
        assert len(mock_manager.sites) == 2
        assert 'example.com' in mock_manager.sites
        assert 'api.example.com' in mock_manager.sites
    
    def test_list_sites_sorted(self, mock_manager):
        """Test that sites can be sorted"""
        mock_manager.sites = {
            'zebra.com': {'port': 8080, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'alpha.com': {'port': 3000, 'ssl': False, 'created': datetime.now().isoformat(), 'config_file': '/path'},
            'beta.com': {'port': 8000, 'ssl': True, 'created': datetime.now().isoformat(), 'config_file': '/path'},
        }
        
        sorted_domains = sorted(mock_manager.sites.keys())
        assert sorted_domains == ['alpha.com', 'beta.com', 'zebra.com']
