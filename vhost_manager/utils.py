"""
Utility functions for Apache Virtual Host Manager
"""
import os
import logging
import subprocess

def setup_logging():
    """Setup logging configuration"""
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
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
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

def check_sudo():
    """Check if script is running with sudo privileges"""
    if os.geteuid() != 0:
        print("❌ This operation requires sudo privileges")
        print("💡 Please run with: sudo python3 manage.py ...")
        exit(1)
