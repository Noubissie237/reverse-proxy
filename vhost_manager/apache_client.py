"""
Client pour communiquer avec l'Apache Agent sur l'hôte
"""
import socket
import json
import logging

logger = logging.getLogger(__name__)

SOCKET_PATH = "/var/run/apache-agent.sock"


class ApacheAgentClient:
    """Client pour communiquer avec l'Apache Agent"""
    
    def __init__(self, socket_path=SOCKET_PATH):
        self.socket_path = socket_path
    
    def _send_request(self, action, params=None):
        """Send request to Apache Agent"""
        try:
            # Create socket
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(30)
            
            # Connect
            client.connect(self.socket_path)
            
            # Send request
            request = {
                'action': action,
                'params': params or {}
            }
            client.sendall(json.dumps(request).encode('utf-8'))
            
            # Receive response
            response = client.recv(4096).decode('utf-8')
            result = json.loads(response)
            
            client.close()
            return result
            
        except FileNotFoundError:
            logger.error(f"Apache Agent socket not found: {self.socket_path}")
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Apache Agent not running',
                'returncode': -1
            }
        except Exception as e:
            logger.error(f"Error communicating with Apache Agent: {e}")
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def a2ensite(self, domain):
        """Enable Apache site"""
        return self._send_request('a2ensite', {'domain': domain})
    
    def a2dissite(self, domain):
        """Disable Apache site"""
        return self._send_request('a2dissite', {'domain': domain})
    
    def a2enmod(self, module):
        """Enable Apache module"""
        return self._send_request('a2enmod', {'module': module})
    
    def reload_apache(self):
        """Reload Apache configuration"""
        return self._send_request('apache_reload')
    
    def restart_apache(self):
        """Restart Apache"""
        return self._send_request('apache_restart')
    
    def test_config(self):
        """Test Apache configuration"""
        return self._send_request('apache_configtest')
    
    def check_status(self):
        """Check if Apache is running"""
        return self._send_request('apache_status')


# Instance globale
apache_client = ApacheAgentClient()
