"""
Apache Virtual Host Manager - Modular Package

A comprehensive tool for managing Apache Virtual Hosts with automatic
SSL certificate installation and configuration.
"""

from .core import ApacheVHostManager
from .config import ConfigManager
from .validation import (
    validate_domain,
    validate_port,
    is_wildcard_domain,
    get_base_domain,
    validate_wildcard_domain,
    get_validated_email
)
from .ssl import (
    install_ssl_certificate,
    install_wildcard_ssl_certificate,
    renew_ssl_certificates,
    check_domain_dns
)
from .monitoring import (
    show_status,
    check_ssl_certificates,
    show_stats,
    check_site_status,
    get_ssl_certificate_info
)
from .utils import setup_logging, run_command, check_sudo

__version__ = "1.5.0"
__all__ = [
    'ApacheVHostManager',
    'ConfigManager',
    'validate_domain',
    'validate_port',
    'is_wildcard_domain',
    'get_base_domain',
    'validate_wildcard_domain',
    'get_validated_email',
    'install_ssl_certificate',
    'install_wildcard_ssl_certificate',
    'renew_ssl_certificates',
    'check_domain_dns',
    'show_status',
    'check_ssl_certificates',
    'show_stats',
    'check_site_status',
    'get_ssl_certificate_info',
    'setup_logging',
    'run_command',
    'check_sudo',
]
