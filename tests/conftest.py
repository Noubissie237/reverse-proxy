"""
Pytest configuration and fixtures
"""
import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def mock_manager():
    """Create a mock VHostManager without initialization"""
    from vhost_manager.core import ApacheVHostManager
    manager = ApacheVHostManager.__new__(ApacheVHostManager)
    manager.sites = {}
    return manager

@pytest.fixture
def sample_site_config():
    """Sample site configuration"""
    return {
        'port': 8080,
        'ssl': True,
        'created': '2024-11-15T10:30:00',
        'config_file': '/etc/apache2/sites-available/example.com.conf'
    }
