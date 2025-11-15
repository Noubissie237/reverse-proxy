#!/usr/bin/env python3
"""
Test script for monitoring features
Creates mock data to test the monitoring commands
"""

import json
import os
from datetime import datetime

# Create a test configuration file
test_config = {
    "example.com": {
        "port": 8080,
        "ssl": True,
        "created": datetime.now().isoformat(),
        "config_file": "/etc/apache2/sites-available/example.com.conf"
    },
    "api.example.com": {
        "port": 3000,
        "ssl": True,
        "created": datetime.now().isoformat(),
        "config_file": "/etc/apache2/sites-available/api.example.com.conf"
    },
    "dev.example.com": {
        "port": 8000,
        "ssl": False,
        "created": datetime.now().isoformat(),
        "config_file": "/etc/apache2/sites-available/dev.example.com.conf"
    }
}

# Save to a test file
test_file = "/tmp/vhost_manager_test.json"
with open(test_file, 'w') as f:
    json.dump(test_config, f, indent=2)

print(f"✅ Test configuration created: {test_file}")
print(f"📊 Sites configured: {len(test_config)}")
print("\nTo test with this configuration, temporarily modify vhost_manager.py:")
print(f"  self.config_file = '{test_file}'")
print("\nOr test the commands with your actual configuration:")
print("  python3 vhost_manager.py status")
print("  python3 vhost_manager.py check-ssl")
print("  python3 vhost_manager.py stats")
