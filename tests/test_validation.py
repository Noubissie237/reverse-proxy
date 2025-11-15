"""
Tests for validation functions (email, port, domain)
"""
import pytest
from email_validator import EmailNotValidError


class TestEmailValidation:
    """Test email validation"""
    
    def test_valid_emails(self):
        """Test that valid emails are accepted"""
        from email_validator import validate_email
        
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "user+tag@example.com",
            "admin@subdomain.example.com",
        ]
        
        for email in valid_emails:
            result = validate_email(email, check_deliverability=False)
            assert result.email == email.lower()
    
    def test_invalid_emails(self):
        """Test that invalid emails are rejected"""
        from email_validator import validate_email
        
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "user@",
            "user name@example.com",
            "",
        ]
        
        for email in invalid_emails:
            with pytest.raises(EmailNotValidError):
                validate_email(email, check_deliverability=False)


class TestPortValidation:
    """Test port validation"""
    
    def test_valid_ports(self):
        """Test that valid ports are accepted"""
        from vhost_manager.validation import validate_port
        
        valid_ports = [
            ("80", 80),
            ("443", 443),
            ("8080", 8080),
            ("3000", 3000),
            ("65535", 65535),
            ("1", 1),
        ]
        
        for port_str, expected in valid_ports:
            result = validate_port(port_str)
            assert result == expected
    
    def test_invalid_ports(self):
        """Test that invalid ports are rejected"""
        from vhost_manager.validation import validate_port
        
        invalid_ports = ["0", "65536", "-1", "abc", "12.34", ""]
        
        for port_str in invalid_ports:
            result = validate_port(port_str)
            assert result is None
    
    def test_port_range(self):
        """Test port range boundaries"""
        from vhost_manager.validation import validate_port
        
        assert validate_port("1") == 1
        assert validate_port("65535") == 65535
        assert validate_port("0") is None
        assert validate_port("65536") is None


class TestDomainValidation:
    """Test domain validation"""
    
    def test_valid_domains(self):
        """Test that valid domains are accepted"""
        from vhost_manager.validation import validate_domain
        
        valid_domains = [
            "example.com",
            "subdomain.example.com",
            "api.v1.example.com",
            "example-site.com",
            "123.example.com",
            "a.b.c.d.example.com",
        ]
        
        for domain in valid_domains:
            assert validate_domain(domain) is True
    
    def test_invalid_domains(self):
        """Test that invalid domains are rejected"""
        from vhost_manager.validation import validate_domain
        
        invalid_domains = [
            "-example.com",
            "example-.com",
            "example..com",
            "",
            "a" * 254,  # Too long
            ".example.com",
            "example.com.",
        ]
        
        for domain in invalid_domains:
            assert validate_domain(domain) is False
    
    def test_domain_length(self):
        """Test domain length validation"""
        from vhost_manager.validation import validate_domain
        
        # Valid length (253 chars max)
        valid_domain = "a" * 63 + "." + "b" * 63 + "." + "c" * 63 + "." + "d" * 59
        assert len(valid_domain) <= 253
        assert validate_domain(valid_domain) is True
        
        # Invalid length (> 253 chars)
        invalid_domain = "a" * 254
        assert validate_domain(invalid_domain) is False
