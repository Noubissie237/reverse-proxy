#!/usr/bin/env python3
"""
Simple test script for validation functions
"""

import re
from email_validator import validate_email, EmailNotValidError

def validate_domain(domain):
    """Validate domain name format (copied from vhost_manager.py)"""
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    
    if not re.match(domain_pattern, domain):
        return False
    
    if len(domain) > 253:
        return False
    
    if domain.startswith('-') or domain.endswith('-'):
        return False
    
    return True

def validate_port(port):
    """Validate port number (copied from vhost_manager.py)"""
    try:
        port_num = int(port)
        if 1 <= port_num <= 65535:
            return port_num
        else:
            return None
    except ValueError:
        return None

def test_email_validation():
    """Test email validation"""
    print("🧪 Testing Email Validation")
    print("=" * 50)
    
    test_cases = [
        ("user@example.com", True),
        ("test.user@domain.co.uk", True),
        ("invalid.email", False),
        ("@example.com", False),
        ("user@", False),
        ("user name@example.com", False),
        ("user+tag@example.com", True),
    ]
    
    passed = 0
    failed = 0
    
    for email, should_be_valid in test_cases:
        try:
            valid = validate_email(email, check_deliverability=False)
            is_valid = True
        except EmailNotValidError:
            is_valid = False
        
        if is_valid == should_be_valid:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        expected = "✅" if should_be_valid else "❌"
        actual = "✅" if is_valid else "❌"
        print(f"{status} | {email:30} | Expected: {expected} | Got: {actual}")
    
    print(f"\n📊 Results: {passed} passed, {failed} failed\n")
    return failed == 0

def test_port_validation():
    """Test port validation"""
    print("🧪 Testing Port Validation")
    print("=" * 50)
    
    test_cases = [
        ("8080", 8080),
        ("80", 80),
        ("443", 443),
        ("3000", 3000),
        ("65535", 65535),
        ("1", 1),
        ("0", None),
        ("65536", None),
        ("abc", None),
        ("-1", None),
    ]
    
    passed = 0
    failed = 0
    
    for port_str, expected in test_cases:
        result = validate_port(port_str)
        
        if result == expected:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{status} | Port: {port_str:10} | Expected: {expected} | Got: {result}")
    
    print(f"\n📊 Results: {passed} passed, {failed} failed\n")
    return failed == 0

def test_domain_validation():
    """Test domain validation"""
    print("🧪 Testing Domain Validation")
    print("=" * 50)
    
    test_cases = [
        ("example.com", True),
        ("subdomain.example.com", True),
        ("api.v1.example.com", True),
        ("example-site.com", True),
        ("123.example.com", True),
        ("-example.com", False),
        ("example-.com", False),
        ("example..com", False),
        ("", False),
        ("a" * 254, False),
    ]
    
    passed = 0
    failed = 0
    
    for domain, should_be_valid in test_cases:
        is_valid = validate_domain(domain)
        
        if is_valid == should_be_valid:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        display_domain = domain if len(domain) < 30 else domain[:27] + "..."
        expected = "✅" if should_be_valid else "❌"
        actual = "✅" if is_valid else "❌"
        
        print(f"{status} | {display_domain:30} | Expected: {expected} | Got: {actual}")
    
    print(f"\n📊 Results: {passed} passed, {failed} failed\n")
    return failed == 0

def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("🚀 Running Validation Tests")
    print("=" * 50 + "\n")
    
    all_passed = True
    
    if not test_email_validation():
        all_passed = False
    
    if not test_port_validation():
        all_passed = False
    
    if not test_domain_validation():
        all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")
    print("=" * 50 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
