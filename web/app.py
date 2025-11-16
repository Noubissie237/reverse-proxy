#!/usr/bin/env python3
"""
Apache Virtual Host Manager - Web Interface
Flask application for managing Apache Virtual Hosts via web browser
"""
import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps

# Add parent directory to path to import vhost_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vhost_manager import (
    ApacheVHostManager,
    show_status,
    check_ssl_certificates,
    show_stats,
    check_site_status,
    get_ssl_certificate_info
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize manager
manager = ApacheVHostManager()

# Simple authentication (to be improved with proper auth system)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')  # Change this!


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def check_sudo():
    """Check if running with sudo privileges"""
    return os.geteuid() == 0


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    """Main dashboard"""
    sites = manager.sites
    
    # Calculate statistics
    total_sites = len(sites)
    ssl_sites = sum(1 for config in sites.values() if config.get('ssl', False))
    
    # Count active sites
    active_sites = 0
    for domain in sites.keys():
        status = check_site_status(domain, sites)
        if status['apache_enabled'] and status['port_active']:
            active_sites += 1
    
    # SSL warnings
    ssl_warnings = []
    for domain, config in sites.items():
        if config.get('ssl', False):
            ssl_info = get_ssl_certificate_info(domain)
            if ssl_info and ssl_info['days_remaining'] < 30:
                ssl_warnings.append({
                    'domain': domain,
                    'days': ssl_info['days_remaining']
                })
    
    stats = {
        'total_sites': total_sites,
        'active_sites': active_sites,
        'ssl_sites': ssl_sites,
        'ssl_warnings': len(ssl_warnings),
        'has_sudo': check_sudo()
    }
    
    return render_template('dashboard.html', stats=stats, ssl_warnings=ssl_warnings)


@app.route('/sites')
@login_required
def sites():
    """List all sites"""
    sites_list = []
    
    for domain, config in sorted(manager.sites.items()):
        status = check_site_status(domain, manager.sites)
        
        site_info = {
            'domain': domain,
            'port': config['port'],
            'ssl': config.get('ssl', False),
            'created': datetime.fromisoformat(config['created']).strftime('%Y-%m-%d %H:%M'),
            'apache_enabled': status['apache_enabled'],
            'port_active': status['port_active'],
            'ssl_days_remaining': status.get('ssl_days_remaining'),
            'config_file': config['config_file']
        }
        sites_list.append(site_info)
    
    return render_template('sites.html', sites=sites_list)


@app.route('/sites/create', methods=['GET', 'POST'])
@login_required
def create_site():
    """Create a new site"""
    if not check_sudo():
        flash('Privilèges sudo requis pour créer un site', 'error')
        return redirect(url_for('sites'))
    
    if request.method == 'POST':
        domain = request.form.get('domain')
        port = request.form.get('port')
        ssl = request.form.get('ssl') == 'on'
        
        try:
            # Validate inputs first
            from vhost_manager.validation import validate_domain, validate_port
            
            if not validate_domain(domain):
                flash(f'Nom de domaine invalide : {domain}', 'error')
                return render_template('create_site.html')
            
            port_num = validate_port(port)
            if port_num is None:
                flash(f'Port invalide : {port}', 'error')
                return render_template('create_site.html')
            
            # Check if site already exists
            if domain in manager.sites:
                flash(f'Le site {domain} existe déjà', 'error')
                return render_template('create_site.html')
            
            # Try to create the site
            # Note: create_site uses print() instead of raising exceptions
            # We need to check if it actually worked
            initial_sites = set(manager.sites.keys())
            manager.create_site(domain, port, ssl)
            
            # Reload config to check if site was actually created
            manager.config_manager.load_config()
            manager.sites = manager.config_manager.sites
            
            if domain in manager.sites:
                flash(f'Site {domain} créé avec succès !', 'success')
            else:
                flash(f'Échec de la création du site {domain}. Vérifiez les logs.', 'error')
            
            return redirect(url_for('sites'))
        except Exception as e:
            flash(f'Erreur lors de la création : {str(e)}', 'error')
            return render_template('create_site.html')
    
    return render_template('create_site.html')


@app.route('/sites/<domain>/delete', methods=['POST'])
@login_required
def delete_site(domain):
    """Delete a site"""
    if not check_sudo():
        return jsonify({'success': False, 'error': 'Privilèges sudo requis'}), 403
    
    try:
        manager.delete_site(domain)
        flash(f'Site {domain} supprimé avec succès', 'success')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/monitoring')
@login_required
def monitoring():
    """Monitoring page"""
    sites_status = []
    
    for domain in sorted(manager.sites.keys()):
        status = check_site_status(domain, manager.sites)
        config = manager.sites[domain]
        
        site_status = {
            'domain': domain,
            'port': config['port'],
            'apache_enabled': status['apache_enabled'],
            'port_active': status['port_active'],
            'ssl_enabled': status['ssl_enabled'],
            'ssl_valid': status.get('ssl_valid', False),
            'ssl_days_remaining': status.get('ssl_days_remaining')
        }
        sites_status.append(site_status)
    
    return render_template('monitoring.html', sites=sites_status)


@app.route('/api/sites')
@login_required
def api_sites():
    """API endpoint to get sites list"""
    sites_list = []
    
    for domain, config in manager.sites.items():
        status = check_site_status(domain, manager.sites)
        sites_list.append({
            'domain': domain,
            'port': config['port'],
            'ssl': config.get('ssl', False),
            'status': status
        })
    
    return jsonify(sites_list)


@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint to get statistics"""
    sites = manager.sites
    total_sites = len(sites)
    ssl_sites = sum(1 for config in sites.values() if config.get('ssl', False))
    
    active_sites = 0
    for domain in sites.keys():
        status = check_site_status(domain, sites)
        if status['apache_enabled'] and status['port_active']:
            active_sites += 1
    
    return jsonify({
        'total_sites': total_sites,
        'active_sites': active_sites,
        'ssl_sites': ssl_sites,
        'non_ssl_sites': total_sites - ssl_sites
    })


@app.route('/ssl-check')
@login_required
def ssl_check():
    """SSL certificates check page"""
    ssl_sites = {domain: config for domain, config in manager.sites.items() 
                 if config.get('ssl', False)}
    
    certificates = []
    warnings = []
    errors = []
    
    for domain in sorted(ssl_sites.keys()):
        ssl_info = get_ssl_certificate_info(domain)
        
        if ssl_info is None:
            errors.append(domain)
            certificates.append({
                'domain': domain,
                'status': 'error',
                'message': 'Certificate not found'
            })
            continue
        
        days = ssl_info['days_remaining']
        expiry = ssl_info['expiry_date'].strftime('%Y-%m-%d %H:%M')
        
        if days > 30:
            status = 'valid'
        elif days > 7:
            status = 'warning'
            warnings.append((domain, days))
        elif days > 0:
            status = 'critical'
            warnings.append((domain, days))
        else:
            status = 'expired'
            errors.append(domain)
        
        certificates.append({
            'domain': domain,
            'status': status,
            'days_remaining': days,
            'expiry_date': expiry,
            'issuer': ssl_info.get('issuer', 'Unknown')
        })
    
    summary = {
        'total': len(ssl_sites),
        'valid': len(ssl_sites) - len(warnings) - len(errors),
        'warnings': len(warnings),
        'errors': len(errors)
    }
    
    return render_template('ssl_check.html', 
                         certificates=certificates, 
                         summary=summary,
                         warnings=warnings,
                         errors=errors)


@app.context_processor
def utility_processor():
    """Add utility functions to templates"""
    return {
        'now': datetime.now(),
        'version': manager.VERSION
    }


if __name__ == '__main__':
    import os
    
    # Determine if running in production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    if not is_production:
        # Development mode warnings
        if not check_sudo():
            print("⚠️  Warning: Not running with sudo privileges")
            print("   Some features may not work correctly")
            print()
        
        print("🚀 Starting Apache VHost Manager Web Interface")
        print(f"📍 Access at: http://localhost:5000")
        print(f"👤 Default credentials: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
        print("⚠️  Change default password in production!")
        print()
    
    # Production: no debug, no verbose output
    app.run(host='0.0.0.0', port=5000, debug=not is_production)
