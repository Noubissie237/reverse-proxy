#!/bin/bash

set -e  # Exit on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' 

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

print_header "🔒 Apache SSL Setup with Let's Encrypt"
print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for sudo privileges
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run with sudo privileges"
    echo "Usage: sudo $0"
    exit 1
fi

# Check if Apache2 is installed
if ! command -v apache2 >/dev/null 2>&1; then
    print_error "Apache2 is not installed. Please install Apache2 first:"
    echo "sudo apt update && sudo apt install apache2"
    exit 1
fi

# Check if Apache2 is running
if ! systemctl is-active --quiet apache2; then
    print_warning "Apache2 is not running. Starting Apache2..."
    systemctl start apache2
    systemctl enable apache2
fi

print_success "Apache2 is running"

# Update system packages
print_status "Updating system packages..."
apt update -qq

# Install required packages
print_status "Installing required packages..."
apt install -y software-properties-common curl wget

# Install Certbot
print_status "Installing Certbot (Let's Encrypt client)..."
if command -v snap >/dev/null 2>&1; then
    # Use snap if available (preferred method)
    snap install core; snap refresh core
    snap install --classic certbot
    
    # Create symlink if it doesn't exist
    if [ ! -f /usr/bin/certbot ]; then
        ln -sf /snap/bin/certbot /usr/bin/certbot
    fi
    print_success "Certbot installed via snap"
else
    # Fallback to apt installation
    apt install -y certbot python3-certbot-apache
    print_success "Certbot installed via apt"
fi

# Verify Certbot installation
if ! command -v certbot >/dev/null 2>&1; then
    print_error "Certbot installation failed"
    exit 1
fi

CERTBOT_VERSION=$(certbot --version 2>&1 | head -n1)
print_success "Certbot installed: $CERTBOT_VERSION"

# Configure automatic renewal
print_status "Configuring automatic certificate renewal..."

# Check if systemd timer exists (preferred method for modern systems)
if systemctl list-unit-files | grep -q "certbot.timer\|snap.certbot.renew.timer"; then
    if systemctl is-enabled snap.certbot.renew.timer >/dev/null 2>&1; then
        print_success "Snap Certbot renewal timer is already active"
    elif systemctl is-enabled certbot.timer >/dev/null 2>&1; then
        print_success "System Certbot renewal timer is already active"
    else
        # Enable the timer if it exists but is not enabled
        if systemctl enable snap.certbot.renew.timer >/dev/null 2>&1; then
            print_success "Enabled snap Certbot renewal timer"
        elif systemctl enable certbot.timer >/dev/null 2>&1; then
            print_success "Enabled system Certbot renewal timer"
        fi
    fi
else
    # Fallback to cron job
    print_status "Setting up cron-based renewal..."
    CRON_LINE="0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload apache2' 2>&1 | logger -t certbot-renew"
    
    # Add cron job if it doesn't exist
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
        print_success "Cron job for certificate renewal configured"
    else
        print_success "Cron job for certificate renewal already exists"
    fi
fi

# Configure firewall if UFW is active
if command -v ufw >/dev/null 2>&1 && ufw status | grep -q "Status: active"; then
    print_status "Configuring UFW firewall..."
    ufw allow 'Apache Full' >/dev/null 2>&1
    
    # Remove the basic Apache rule if it exists
    if ufw status | grep -q "Apache"; then
        ufw delete allow 'Apache' >/dev/null 2>&1 || true
    fi
    
    print_success "UFW firewall configured for Apache Full (HTTP + HTTPS)"
elif command -v iptables >/dev/null 2>&1; then
    print_status "Checking iptables configuration..."
    
    # Check if ports are already open
    if ! iptables -L INPUT -n | grep -q "dpt:80"; then
        print_warning "Port 80 (HTTP) may not be open in iptables"
        echo "Consider running: sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT"
    fi
    
    if ! iptables -L INPUT -n | grep -q "dpt:443"; then
        print_warning "Port 443 (HTTPS) may not be open in iptables"
        echo "Consider running: sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT"
    fi
fi

# Enable required Apache modules
print_status "Enabling required Apache modules..."
MODULES=("rewrite" "ssl" "headers" "proxy" "proxy_http")

for module in "${MODULES[@]}"; do
    if a2enmod "$module" >/dev/null 2>&1; then
        print_success "Enabled Apache module: $module"
    else
        print_warning "Module $module may already be enabled"
    fi
done

# Reload Apache to apply module changes
systemctl reload apache2

# Test Certbot
print_status "Testing Certbot configuration..."
if certbot --version >/dev/null 2>&1; then
    print_success "Certbot is working correctly"
else
    print_error "Certbot test failed"
    exit 1
fi

# Create log directory for custom logging
mkdir -p /var/log/vhost-manager
touch /var/log/vhost-manager/setup.log
chmod 644 /var/log/vhost-manager/setup.log

# Log setup completion
echo "$(date): SSL setup completed successfully" >> /var/log/vhost-manager/setup.log

# Print completion message
echo ""
print_header "✅ SSL Setup Completed Successfully!"
print_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_success "What's been configured:"
echo "  🔧 Certbot (Let's Encrypt client) installed"
echo "  ⏰ Automatic certificate renewal configured"
echo "  🔥 Firewall configured for HTTPS"
echo "  📦 Required Apache modules enabled"
echo ""
print_header "💡 Next Steps:"
echo "  1. Create your first Virtual Host:"
echo "     ${CYAN}sudo python3 vhost_manager.py create yourdomain.com 8080${NC}"
echo ""
echo "  2. The script will automatically:"
echo "     • Create Apache Virtual Host configuration"
echo "     • Install SSL certificate"
echo "     • Configure HTTPS redirect"
echo ""
print_header "📚 Useful Commands:"
echo "  • View certificates: ${CYAN}sudo certbot certificates${NC}"
echo "  • Renew certificates: ${CYAN}sudo certbot renew${NC}"
echo "  • Test renewal: ${CYAN}sudo certbot renew --dry-run${NC}"
echo "  • Apache status: ${CYAN}sudo systemctl status apache2${NC}"
echo ""
print_header "📖 Documentation:"
echo "  GitHub: ${CYAN}https://github.com/Noubissie237/reverse-proxy${NC}"
echo ""