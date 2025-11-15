#!/usr/bin/env python3
"""
Apache Virtual Host Manager - CLI Interface

Main command-line interface for managing Apache Virtual Hosts
"""
import sys
from vhost_manager import (
    ApacheVHostManager,
    setup_logging,
    is_wildcard_domain,
    install_wildcard_ssl_certificate,
    renew_ssl_certificates,
    show_status,
    check_ssl_certificates,
    show_stats
)

# Setup logging
logger = setup_logging()


def main():
    """Main function to handle command line arguments"""
    manager = ApacheVHostManager()
    
    if len(sys.argv) < 2:
        print("Apache Virtual Host Manager")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Usage:")
        print("  sudo python3 manage.py create <domain> <port> [--no-ssl]")
        print("  sudo python3 manage.py delete <domain>")
        print("  python3 manage.py list")
        print("  python3 manage.py status")
        print("  python3 manage.py check-ssl")
        print("  python3 manage.py stats")
        print("  sudo python3 manage.py renew-ssl")
        print("  sudo python3 manage.py install-wildcard-ssl <domain>")
        print("  python3 manage.py version")
        print()
        print("Examples:")
        print("  sudo python3 manage.py create mysite.com 8080")
        print("  sudo python3 manage.py create '*.example.com' 8080")
        print("  sudo python3 manage.py create api.example.com 3000 --no-ssl")
        print("  sudo python3 manage.py install-wildcard-ssl '*.example.com'")
        print("  sudo python3 manage.py delete mysite.com")
        print("  python3 manage.py list")
        print("  python3 manage.py status")
        print("  python3 manage.py check-ssl")
        sys.exit(1)
    
    action = sys.argv[1]
    
    try:
        if action == "create":
            if len(sys.argv) < 4:
                print("Usage: sudo python3 manage.py create <domain> <port> [--no-ssl]")
                sys.exit(1)
            domain = sys.argv[2]
            port = sys.argv[3]
            ssl = "--no-ssl" not in sys.argv
            manager.create_site(domain, port, ssl)
        
        elif action == "delete":
            if len(sys.argv) != 3:
                print("Usage: sudo python3 manage.py delete <domain>")
                sys.exit(1)
            domain = sys.argv[2]
            manager.delete_site(domain)
        
        elif action == "list":
            manager.list_sites()
        
        elif action == "status":
            show_status(manager.sites)
        
        elif action == "check-ssl":
            check_ssl_certificates(manager.sites)
        
        elif action == "stats":
            show_stats(manager.sites)
        
        elif action == "renew-ssl":
            renew_ssl_certificates()
        
        elif action == "install-wildcard-ssl":
            if len(sys.argv) != 3:
                print("Usage: sudo python3 manage.py install-wildcard-ssl <wildcard-domain>")
                print("Example: sudo python3 manage.py install-wildcard-ssl '*.example.com'")
                sys.exit(1)
            wildcard_domain = sys.argv[2]
            if not is_wildcard_domain(wildcard_domain):
                print(f"❌ Domain must be a wildcard domain (e.g., *.example.com)")
                print(f"   Provided: {wildcard_domain}")
                sys.exit(1)
            install_wildcard_ssl_certificate(wildcard_domain)
        
        elif action == "version":
            manager.show_version()
        
        else:
            print(f"Unknown action: {action}")
            print("Available actions: create, delete, list, status, check-ssl, stats, renew-ssl, install-wildcard-ssl, version")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ An unexpected error occurred: {e}")
        print("Please check the logs for more details: /var/log/vhost-manager/manager.log")
        sys.exit(1)


if __name__ == "__main__":
    main()
