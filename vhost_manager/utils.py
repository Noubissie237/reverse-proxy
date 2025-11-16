"""
Utility functions for Apache Virtual Host Manager
"""
import os
import sys
import logging
import subprocess

# Try to import Apache client (for Docker mode)
try:
    from .apache_client import apache_client
    USE_APACHE_AGENT = True
except ImportError:
    USE_APACHE_AGENT = False

def setup_logging(verbose=None):
    """
    Setup logging configuration
    
    Args:
        verbose (bool): If True, log to console. If None, check VHOST_VERBOSE env var
    """
    # Check environment variable if verbose not explicitly set
    if verbose is None:
        verbose = os.environ.get('VHOST_VERBOSE', '1') == '1'
    
    log_dir = "/var/log/vhost-manager"
    
    # Try to create log directory, fallback to local if permission denied
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_file = f'{log_dir}/manager.log'
    except PermissionError:
        # Fallback to local directory for non-root users
        log_dir = os.path.expanduser("~/.vhost-manager/logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = f'{log_dir}/manager.log'
    
    # Setup handlers
    handlers = [logging.FileHandler(log_file)]
    
    # Only add console handler if verbose mode
    if verbose:
        handlers.append(logging.StreamHandler())
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Override any existing config
    )
    return logging.getLogger(__name__)

def run_command(command, show_output=False):
    """
    Execute a shell command
    
    Args:
        command (str): Command to execute
        show_output (bool): Whether to show command output
        
    Returns:
        bool: True if command succeeded, False otherwise
    """
    # Check if we should use Apache Agent (Docker mode)
    if USE_APACHE_AGENT and os.path.exists('/var/run/apache-agent.sock'):
        return run_command_via_agent(command, show_output)
    
    # Direct execution (non-Docker mode)
    try:
        if show_output:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                env={**os.environ, 'PAGER': 'cat'}
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                env={**os.environ, 'PAGER': 'cat'}
            )
        return True
    except subprocess.CalledProcessError:
        return False


def run_command_via_agent(command, show_output=False):
    """
    Execute command via Apache Agent (for Docker mode)
    
    Args:
        command (str): Command to execute
        show_output (bool): Whether to show command output
        
    Returns:
        bool: True if command succeeded, False otherwise
    """
    # Parse command to determine action
    parts = command.split()
    if not parts:
        return False
    
    cmd = parts[0]
    
    try:
        if cmd == 'a2ensite':
            domain = parts[1] if len(parts) > 1 else ''
            result = apache_client.a2ensite(domain)
        elif cmd == 'a2dissite':
            domain = parts[1] if len(parts) > 1 else ''
            result = apache_client.a2dissite(domain)
        elif cmd == 'a2enmod':
            module = parts[1] if len(parts) > 1 else ''
            result = apache_client.a2enmod(module)
        elif 'systemctl reload apache2' in command:
            result = apache_client.reload_apache()
        elif 'systemctl restart apache2' in command:
            result = apache_client.restart_apache()
        elif 'apache2ctl configtest' in command:
            result = apache_client.test_config()
        elif 'systemctl is-active apache2' in command:
            result = apache_client.check_status()
        else:
            # Fallback to direct execution for other commands
            return subprocess.run(command, shell=True, check=True, capture_output=not show_output).returncode == 0
        
        if show_output and result.get('stdout'):
            print(result['stdout'])
        if show_output and result.get('stderr'):
            print(result['stderr'], file=sys.stderr)
        
        return result.get('success', False)
        
    except Exception as e:
        logging.error(f"Error executing command via agent: {e}")
        return False

def check_sudo():
    """Check if script is running with sudo privileges"""
    if os.geteuid() != 0:
        print("❌ This operation requires sudo privileges")
        print("💡 Please run with: sudo python3 manage.py ...")
        exit(1)
