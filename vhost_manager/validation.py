"""
Validation functions for domains, ports, emails, and wildcards
"""
import re
import os
from email_validator import validate_email, EmailNotValidError


def validate_domain(domain):
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


def validate_port(port):
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
        print(f"❌ Invalid port: {port}")
        return None


def is_wildcard_domain(domain):
    """
    Check if domain is a wildcard domain
    
    Args:
        domain (str): Domain name to check
        
    Returns:
        bool: True if wildcard domain, False otherwise
    """
    return domain.startswith('*.')


def get_base_domain(domain):
    """
    Extract base domain from wildcard domain
    
    Args:
        domain (str): Domain name (may be wildcard)
        
    Returns:
        str: Base domain without wildcard prefix
    """
    if is_wildcard_domain(domain):
        return domain[2:]  # Remove '*.'
    return domain


def validate_wildcard_domain(domain):
    """
    Validate wildcard domain format
    
    Args:
        domain (str): Wildcard domain to validate
        
    Returns:
        bool: True if valid wildcard domain, False otherwise
    """
    if not is_wildcard_domain(domain):
        return False
    
    # Extract base domain and validate it
    base_domain = get_base_domain(domain)
    return validate_domain(base_domain)


def get_validated_email():
    """
    Get and validate email for Let's Encrypt
    
    Returns:
        str: Validated email address
    """
    email_file = "/etc/letsencrypt/.email"
    
    # Check if email already exists
    if os.path.exists(email_file):
        try:
            with open(email_file, 'r') as f:
                saved_email = f.read().strip()
            
            # Validate saved email
            valid = validate_email(saved_email, check_deliverability=False)
            print(f"📧 Using saved email: {valid.email}")
            return valid.email
        except (EmailNotValidError, IOError):
            pass
    
    # Prompt for new email
    while True:
        print("\n📧 Let's Encrypt requires an email for certificate notifications")
        email = input("Enter your email address: ").strip()
        
        if not email:
            print("❌ Email cannot be empty")
            continue
        
        try:
            # Validate and normalize email
            valid = validate_email(email, check_deliverability=False)
            normalized_email = valid.email
            
            # Save for future use
            os.makedirs(os.path.dirname(email_file), exist_ok=True)
            with open(email_file, 'w') as f:
                f.write(normalized_email)
            os.chmod(email_file, 0o644)
            
            print(f"✅ Email validated: {normalized_email}")
            return normalized_email
            
        except EmailNotValidError as e:
            print(f"❌ Invalid email: {e}")
            print("💡 Example: user@example.com")
            print()
