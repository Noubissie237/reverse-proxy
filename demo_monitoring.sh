#!/bin/bash

# Demo script for monitoring features
# This creates a temporary test configuration and demonstrates the monitoring commands

echo "🎬 Apache Virtual Host Manager - Monitoring Demo"
echo "=================================================="
echo ""

# Create test configuration
python3 test_monitoring.py

echo ""
echo "📋 Testing 'list' command:"
echo "-------------------------------------------"
python3 -c "
import sys
sys.path.insert(0, '.')
from vhost_manager import ApacheVHostManager

manager = ApacheVHostManager()
manager.config_file = '/tmp/vhost_manager_test.json'
manager.load_config()
manager.list_sites()
"

echo ""
echo "📊 Testing 'status' command:"
echo "-------------------------------------------"
python3 -c "
import sys
sys.path.insert(0, '.')
from vhost_manager import ApacheVHostManager

manager = ApacheVHostManager()
manager.config_file = '/tmp/vhost_manager_test.json'
manager.load_config()
manager.show_status()
"

echo ""
echo "📈 Testing 'stats' command:"
echo "-------------------------------------------"
python3 -c "
import sys
sys.path.insert(0, '.')
from vhost_manager import ApacheVHostManager

manager = ApacheVHostManager()
manager.config_file = '/tmp/vhost_manager_test.json'
manager.load_config()
manager.show_stats()
"

echo ""
echo "🔒 Testing 'check-ssl' command:"
echo "-------------------------------------------"
python3 -c "
import sys
sys.path.insert(0, '.')
from vhost_manager import ApacheVHostManager

manager = ApacheVHostManager()
manager.config_file = '/tmp/vhost_manager_test.json'
manager.load_config()
manager.check_ssl_certificates()
"

echo ""
echo "✅ Demo completed!"
echo ""
echo "💡 To use these commands with your actual sites:"
echo "   python3 vhost_manager.py status"
echo "   python3 vhost_manager.py check-ssl"
echo "   python3 vhost_manager.py stats"
