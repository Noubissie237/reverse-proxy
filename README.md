# 🌐 Apache Virtual Host Manager

**Automated Apache Virtual Host Manager with SSL/HTTPS**

Automate the creation of Apache Virtual Hosts with automatic HTTPS redirect and free SSL certificates via Let's Encrypt.

## 🚀 Features

- ✅ **Automated creation** of Apache Virtual Hosts
- ✅ **Automatic SSL/HTTPS** with Let's Encrypt (free certificates)
- ✅ **Automatic HTTP → HTTPS redirect**
- ✅ **Reverse proxy** to any local port
- ✅ **Complete management**: create, delete, list sites
- ✅ **Separate logs** per domain
- ✅ **Automatic renewal** of SSL certificates
- ✅ **Security headers** included

## 📋 Prerequisites

- **Linux Server** (Ubuntu/Debian recommended)
- **Apache2** installed and configured
- **Sudo privileges**
- **DNS configured** (A record pointing to your server)
- **Ports 80 and 443 open** in firewall

## 📦 Installation

### 1. Download the scripts

```bash
# Download the Python manager
wget https://raw.githubusercontent.com/Noubissie237/reverse-proxy/main/vhost_manager.py

# Download the SSL setup script
wget https://raw.githubusercontent.com/Noubissie237/reverse-proxy/main/setup_ssl.sh

# Make scripts executable
chmod +x setup_ssl.sh
chmod +x vhost_manager.py
```

### 2. Initial SSL configuration (one time only)

```bash
sudo ./setup_ssl.sh
```

This command:
- Installs Certbot (Let's Encrypt)
- Configures automatic certificate renewal
- Configures firewall if necessary

## 🎯 Usage

### Create a new site

```bash
sudo python3 vhost_manager.py create <domain> <port>
```

**Example:**
```bash
sudo python3 vhost_manager.py create mysite.com 8080
```

The script will ask you:
1. Your email (for Let's Encrypt, first time only)
2. Whether you want to install SSL certificate (recommended: y)

### List all sites

```bash
python3 vhost_manager.py list
```

### Delete a site

```bash
sudo python3 vhost_manager.py delete <domain>
```

### Renew SSL certificates

```bash
sudo python3 vhost_manager.py renew-ssl
```

### Create a site without SSL

```bash
sudo python3 vhost_manager.py create <domain> <port> --no-ssl
```

## 📖 Practical Examples

### Example 1: E-commerce site

```bash
# Create an e-commerce site on port 3000
sudo python3 vhost_manager.py create shop.com 3000
```

**Result:**
- `http://shop.com` → redirects to `https://shop.com`
- `https://shop.com` → proxies to `localhost:3000`
- Automatic and valid SSL certificate

### Example 2: Backend API

```bash
# API on port 8080
sudo python3 vhost_manager.py create api.myapp.com 8080
```

### Example 3: React Application

```bash
# React app in development on port 3000
sudo python3 vhost_manager.py create app.example.com 3000
```

## 📂 Generated file structure

```
/etc/apache2/sites-available/
├── mysite.com.conf            # Apache configuration
└── api.myapp.com.conf         # Apache configuration

/var/log/apache2/
├── mysite.com-access.log      # Access logs
├── mysite.com-error.log       # Error logs
├── mysite.com-ssl-access.log  # HTTPS logs
└── mysite.com-ssl-error.log   # HTTPS error logs

/etc/letsencrypt/live/
├── mysite.com/                # SSL certificates
└── api.myapp.com/             # SSL certificates

/etc/vhost_manager.json        # Manager configuration
```

## 🔧 Advanced Configuration

### Modify site configuration

Configuration files are located in `/etc/apache2/sites-available/`. You can edit them manually:

```bash
sudo nano /etc/apache2/sites-available/mysite.com.conf
sudo systemctl reload apache2
```

### Security headers included

Each HTTPS site is configured with:
- `Strict-Transport-Security` (HSTS)
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`

### Logs and monitoring

```bash
# View logs in real-time
sudo tail -f /var/log/apache2/mysite.com-access.log

# Check SSL errors
sudo tail -f /var/log/apache2/mysite.com-ssl-error.log
```

## 🔄 Complete Workflow

### Setting up a new domain

1. **Configure DNS**: Create an A record pointing to your server
2. **Wait for DNS propagation** (few minutes to few hours)
3. **Create the Virtual Host**:
   ```bash
   sudo python3 vhost_manager.py create newsite.com 8080
   ```
4. **Test**: Navigate to `https://newsite.com`

### Verification

```bash
# Verify site is active
sudo a2ensite
apache2ctl -S

# Test configuration
sudo apache2ctl configtest

# Check certificates
sudo certbot certificates
```

## 🛠️ Troubleshooting

### Error "DNS not found"
- Verify your DNS A record points to your server
- Wait for DNS propagation (test with `dig mysite.com`)

### SSL certificate error
```bash
# Check Let's Encrypt logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Force renewal
sudo certbot renew --force-renewal
```

### Site inaccessible
```bash
# Check if service on port is running
curl localhost:8080

# Check Apache logs
sudo tail -f /var/log/apache2/error.log
```

### Port already in use
```bash
# See which ports are in use
sudo netstat -tulpn | grep :8080
sudo lsof -i :8080
```

## 📚 Useful Commands

```bash
# List all active Apache sites
sudo a2ensite

# Disable a site
sudo a2dissite mysite.com

# Reload Apache
sudo systemctl reload apache2

# Restart Apache
sudo systemctl restart apache2

# View Apache status
sudo systemctl status apache2

# Test Apache configuration
sudo apache2ctl configtest

# View configured Virtual Hosts
sudo apache2ctl -S
```

## 🔐 Security

### Best practices included

- **Forced HTTPS**: Automatic HTTP → HTTPS redirect
- **HSTS enabled**: Protection against downgrade attacks
- **Security headers**: XSS and clickjacking protection
- **Separate logs**: Per-domain monitoring
- **Valid certificates**: Let's Encrypt recognized by all browsers

### Recommended firewall

```bash
# With UFW
sudo ufw allow 'Apache Full'
sudo ufw allow ssh
sudo ufw enable

# With iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

## 🔄 Automatic Certificate Renewal

The SSL setup script configures automatic renewal via:
- **Systemd timer** (Ubuntu 20.04+)
- **Cron job** (fallback)

Certificates are renewed automatically every 90 days. You can manually check renewal:

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal
```

## 📊 Monitoring and Maintenance

### Check site status

```bash
# Check all managed sites
python3 vhost_manager.py list

# Check Apache Virtual Hosts
sudo apache2ctl -S

# Check SSL certificate expiration
sudo certbot certificates
```

### Log monitoring

```bash
# Monitor all Apache logs
sudo tail -f /var/log/apache2/*.log

# Monitor specific domain
sudo tail -f /var/log/apache2/mysite.com-*.log

# Check for SSL/TLS errors
sudo grep -i ssl /var/log/apache2/error.log
```

## 🚀 Performance Tips

### Optimize Apache configuration

```bash
# Enable compression
sudo a2enmod deflate

# Enable caching
sudo a2enmod expires
sudo a2enmod headers

# Reload Apache
sudo systemctl reload apache2
```

### Monitor resource usage

```bash
# Check Apache processes
ps aux | grep apache2

# Monitor server resources
htop
```

## 📞 Support and Debugging

### Check versions

```bash
apache2 -v
certbot --version
python3 --version
```

### Important logs

```bash
# General Apache logs
sudo tail -f /var/log/apache2/error.log

# Let's Encrypt logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# System logs
sudo journalctl -u apache2 -f
```

### Common issues and solutions

| Issue | Solution |
|-------|----------|
| "Permission denied" | Run with `sudo` |
| "Port already in use" | Check with `lsof -i :PORT` |
| "Domain validation failed" | Verify DNS A record |
| "Certificate expired" | Run `sudo certbot renew` |
| "Site not accessible" | Check Apache status and logs |

## 🔧 Customization

### Add custom configuration

You can modify the generated Apache configuration files:

```bash
# Edit site configuration
sudo nano /etc/apache2/sites-available/mysite.com.conf

# Add custom directives, then reload
sudo systemctl reload apache2
```

### Environment-specific settings

For development environments, you might want to:

```bash
# Create site without SSL
sudo python3 vhost_manager.py create dev.mysite.com 3000 --no-ssl

# Use different ports for different environments
sudo python3 vhost_manager.py create staging.mysite.com 3001
sudo python3 vhost_manager.py create prod.mysite.com 3002
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request to the [reverse-proxy repository](https://github.com/Noubissie237/reverse-proxy).

## 📞 Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Open an issue on [GitHub](https://github.com/Noubissie237/reverse-proxy/issues)

---

**💡 Pro Tip:** Add this alias to your `.bashrc` for easier usage:
```bash
alias vhost='sudo python3 /path/to/vhost_manager.py'
```

Then simply use:
```bash
vhost create mysite.com 8080
vhost list
vhost delete mysite.com
```

---

**⭐ Star this repository** if it helped you manage your Apache Virtual Hosts more efficiently!