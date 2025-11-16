#!/usr/bin/env python3
"""
Apache Agent - Service qui écoute les commandes du conteneur Docker
et les exécute sur l'hôte avec les privilèges appropriés
"""
import socket
import os
import subprocess
import json
import logging
from pathlib import Path

# Configuration
SOCKET_PATH = "/var/run/apache-agent.sock"
LOG_FILE = "/var/log/vhost-manager/apache-agent.log"

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def execute_command(command):
    """Execute a shell command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timeout',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }


def handle_request(data):
    """Handle incoming request from container"""
    try:
        request = json.loads(data)
        action = request.get('action')
        params = request.get('params', {})
        
        logger.info(f"Received action: {action} with params: {params}")
        
        if action == 'a2ensite':
            domain = params.get('domain')
            result = execute_command(f"a2ensite {domain}")
            
        elif action == 'a2dissite':
            domain = params.get('domain')
            result = execute_command(f"a2dissite {domain}")
            
        elif action == 'a2enmod':
            module = params.get('module')
            result = execute_command(f"a2enmod {module}")
            
        elif action == 'apache_reload':
            result = execute_command("systemctl reload apache2")
            
        elif action == 'apache_restart':
            result = execute_command("systemctl restart apache2")
            
        elif action == 'apache_configtest':
            result = execute_command("apache2ctl configtest")
            
        elif action == 'apache_status':
            result = execute_command("systemctl is-active apache2")
            
        else:
            result = {
                'success': False,
                'stdout': '',
                'stderr': f'Unknown action: {action}',
                'returncode': -1
            }
        
        logger.info(f"Action {action} result: {result['success']}")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Invalid JSON: {str(e)}',
            'returncode': -1
        }
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }


def start_server():
    """Start the Unix socket server"""
    # Remove old socket if exists
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    
    # Create socket
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    
    # Set permissions so container can access it
    os.chmod(SOCKET_PATH, 0o666)
    
    server.listen(5)
    logger.info(f"Apache Agent listening on {SOCKET_PATH}")
    
    try:
        while True:
            conn, _ = server.accept()
            try:
                data = conn.recv(4096).decode('utf-8')
                if data:
                    result = handle_request(data)
                    response = json.dumps(result)
                    conn.sendall(response.encode('utf-8'))
            except Exception as e:
                logger.error(f"Error handling connection: {e}")
            finally:
                conn.close()
    except KeyboardInterrupt:
        logger.info("Shutting down Apache Agent")
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)


if __name__ == '__main__':
    # Check if running as root
    if os.geteuid() != 0:
        print("Error: This script must be run as root")
        exit(1)
    
    logger.info("Starting Apache Agent...")
    start_server()
