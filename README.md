# 🌐 Apache Virtual Host Manager

![Tests](https://github.com/Noubissie237/reverse-proxy/workflows/Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

<details>
<summary>Version Française</summary>

**Gestionnaire automatisé de Virtual Hosts Apache avec SSL/HTTPS**

Automatisez la création de Virtual Hosts Apache avec redirection HTTPS automatique et certificats SSL gratuits via Let's Encrypt.

## 🚀 Fonctionnalités

- ✅ **Création automatisée** de Virtual Hosts Apache
- ✅ **SSL/HTTPS automatique** avec Let's Encrypt (certificats gratuits)
- ✅ **Certificats Wildcard** (`*.example.com`) pour tous les sous-domaines
- ✅ **Redirection automatique HTTP → HTTPS**
- ✅ **Proxy inverse** vers n'importe quel port local
- ✅ **Gestion complète** : créer, supprimer, lister les sites
- ✅ **Monitoring** : statut des sites, vérification SSL, statistiques
- ✅ **Logs séparés** par domaine
- ✅ **Renouvellement automatique** des certificats SSL
- ✅ **En-têtes de sécurité** inclus
- ✅ **Tests automatisés** avec CI/CD

## 📋 Prérequis

- **Serveur Linux** (Ubuntu/Debian recommandé)
- **Apache2** installé et configuré
- **Git** installé (`sudo apt install git`)
- **Python 3.9+** avec pip
- **Privilèges sudo**
- **DNS configuré** (enregistrement A pointant vers votre serveur)
- **Ports 80 et 443 ouverts** dans le pare-feu

## 📦 Installation

### 1. Cloner le dépôt

```bash
# Cloner le dépôt GitHub
git clone https://github.com/Noubissie237/reverse-proxy.git

# Accéder au répertoire
cd reverse-proxy

# Rendre les scripts exécutables
chmod +x setup_ssl.sh
chmod +x manage.py
chmod +x check_dns.py
```

### 2. Installer les dépendances Python

```bash
# Installer les dépendances requises
pip3 install -r requirements.txt
```

Cette commande installe :
- `requests` : Pour les requêtes HTTP
- `email-validator` : Pour la validation des emails

### 3. Configuration SSL initiale (une seule fois)

```bash
sudo ./setup_ssl.sh
```

Cette commande :
- Installe Certbot (Let's Encrypt)
- Configure le renouvellement automatique des certificats
- Configure le pare-feu si nécessaire

## 🎯 Utilisation

### 4. Vérifier la configuration DNS (RECOMMANDÉ)

```bash
python3 check_dns.py <domaine>
```

### 5. Créer un nouveau site

```bash
sudo python3 manage.py create <domaine> <port>
```

**Exemple :**
```bash
sudo python3 manage.py create monsite.com 8080
```

Le script vous demandera :
1. Votre email (pour Let's Encrypt, première fois seulement)
2. Si vous voulez installer le certificat SSL (recommandé : y)

### Lister tous les sites

```bash
python3 manage.py list
```

### Voir le statut détaillé des sites

```bash
python3 manage.py status
```

Affiche pour chaque site :
- Statut Apache (activé/désactivé)
- Statut du service sur le port
- Statut SSL et jours restants avant expiration
- Date de création

### Vérifier les certificats SSL

```bash
python3 manage.py check-ssl
```

Affiche :
- Liste de tous les certificats SSL
- Date d'expiration
- Jours restants
- Alertes si expiration < 30 jours

### Voir les statistiques

```bash
python3 manage.py stats
```

Affiche :
- Nombre total de sites
- Sites actifs vs inactifs
- Répartition SSL/non-SSL
- Distribution des ports

### Supprimer un site

```bash
sudo python3 manage.py delete <domaine>
```

### Renouveler les certificats SSL

```bash
sudo python3 manage.py renew-ssl
```

### Créer un site sans SSL

```bash
sudo python3 manage.py create <domaine> <port> --no-ssl
```

### 🌟 Certificats Wildcard (Nouveau !)

Créer un certificat pour tous les sous-domaines :

```bash
# Créer un site avec wildcard
sudo python3 manage.py create '*.example.com' 8080

# Ou installer uniquement le certificat wildcard
sudo python3 manage.py install-wildcard-ssl '*.example.com'
```

**Avantages :**
- Un seul certificat pour tous les sous-domaines
- `api.example.com`, `app.example.com`, `admin.example.com`, etc.

**Note :** Nécessite validation DNS manuelle (ajout d'un TXT record).  
📚 Voir le guide complet : [WILDCARD_SSL_GUIDE.md](WILDCARD_SSL_GUIDE.md)

## 📖 Exemples Pratiques

### Exemple 1 : Site e-commerce

```bash
# Créer un site e-commerce sur le port 3000
sudo python3 manage.py create boutique.com 3000
```

**Résultat :**
- `http://boutique.com` → redirige vers `https://boutique.com`
- `https://boutique.com` → proxy vers `localhost:3000`
- Certificat SSL automatique et valide

### Exemple 2 : API Backend

```bash
# API sur le port 8080
sudo python3 check_dns.py api.monapp.com
sudo python3 manage.py create api.monapp.com 8080
```

### Exemple 3 : Application React

```bash
# App React en développement sur le port 3000
sudo python3 check_dns.py app.exemple.com
sudo python3 manage.py create app.exemple.com 3000
```

## 📂 Structure des fichiers générés

```
/etc/apache2/sites-available/
├── monsite.com.conf              # Configuration Apache
└── api.monapp.com.conf           # Configuration Apache

/var/log/apache2/
├── monsite.com-access.log        # Logs d'accès
├── monsite.com-error.log         # Logs d'erreur
├── monsite.com-ssl-access.log    # Logs HTTPS
└── monsite.com-ssl-error.log     # Logs d'erreur HTTPS

/etc/letsencrypt/live/
├── monsite.com/                  # Certificats SSL
└── api.monapp.com/               # Certificats SSL

/etc/vhost_manager.json           # Configuration du gestionnaire
```

## 🔧 Configuration Avancée

### Modifier la configuration d'un site

Les fichiers de configuration se trouvent dans `/etc/apache2/sites-available/`. Vous pouvez les éditer manuellement :

```bash
sudo nano /etc/apache2/sites-available/monsite.com.conf
sudo systemctl reload apache2
```

### En-têtes de sécurité inclus

Chaque site HTTPS est configuré avec :
- `Strict-Transport-Security` (HSTS)
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`

### Logs et surveillance

```bash
# Voir les logs en temps réel
sudo tail -f /var/log/apache2/monsite.com-access.log

# Vérifier les erreurs SSL
sudo tail -f /var/log/apache2/monsite.com-ssl-error.log
```

## 🔄 Flux de Travail Complet

### Configuration d'un nouveau domaine

1. **Configurer le DNS** : Créer un enregistrement A pointant vers votre serveur
2. **Attendre la propagation DNS** (quelques minutes à quelques heures)
3. **Créer le Virtual Host** :
   ```bash
   sudo python3 check_dns.py nouveausite.com
   sudo python3 manage.py create nouveausite.com 8080
   ```
4. **Tester** : Naviguer vers `https://nouveausite.com`

### Vérification

```bash
# Vérifier que le site est actif
sudo a2ensite
apache2ctl -S

# Tester la configuration
sudo apache2ctl configtest

# Vérifier les certificats
sudo certbot certificates
```

## 🛠️ Dépannage

### Erreur "DNS not found"
- Vérifiez que votre enregistrement DNS A pointe vers votre serveur
- Attendez la propagation DNS (testez avec `dig monsite.com`)

### Erreur de certificat SSL
```bash
# Vérifier les logs Let's Encrypt
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Forcer le renouvellement
sudo certbot renew --force-renewal
```

### Site inaccessible
```bash
# Vérifier si le service sur le port fonctionne
curl localhost:8080

# Vérifier les logs Apache
sudo tail -f /var/log/apache2/error.log
```

### Port déjà utilisé
```bash
# Voir quels ports sont utilisés
sudo netstat -tulpn | grep :8080
sudo lsof -i :8080
```

## 📚 Commandes Utiles

```bash
# Lister tous les sites Apache actifs
sudo a2ensite

# Désactiver un site
sudo a2dissite monsite.com

# Recharger Apache
sudo systemctl reload apache2

# Redémarrer Apache
sudo systemctl restart apache2

# Voir le statut d'Apache
sudo systemctl status apache2

# Tester la configuration Apache
sudo apache2ctl configtest

# Voir les Virtual Hosts configurés
sudo apache2ctl -S
```

## 🔐 Sécurité

### Bonnes pratiques incluses

- **HTTPS forcé** : Redirection automatique HTTP → HTTPS
- **HSTS activé** : Protection contre les attaques de rétrogradation
- **En-têtes de sécurité** : Protection XSS et clickjacking
- **Logs séparés** : Surveillance par domaine
- **Certificats valides** : Let's Encrypt reconnu par tous les navigateurs

### Pare-feu recommandé

```bash
# Avec UFW
sudo ufw allow 'Apache Full'
sudo ufw allow ssh
sudo ufw enable

# Avec iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

## 🔄 Renouvellement Automatique des Certificats

Le script de configuration SSL configure le renouvellement automatique via :
- **Timer systemd** (Ubuntu 20.04+)
- **Tâche cron** (solution de secours)

Les certificats sont renouvelés automatiquement tous les 90 jours. Vous pouvez vérifier manuellement le renouvellement :

```bash
# Tester le renouvellement (test à blanc)
sudo certbot renew --dry-run

# Forcer le renouvellement
sudo certbot renew --force-renewal
```

## 📊 Surveillance et Maintenance

### Vérifier le statut des sites

```bash
# Vérifier tous les sites gérés
python3 manage.py list

# Vérifier les Virtual Hosts Apache
sudo apache2ctl -S

# Vérifier l'expiration des certificats SSL
sudo certbot certificates
```

### Surveillance des logs

```bash
# Surveiller tous les logs Apache
sudo tail -f /var/log/apache2/*.log

# Surveiller un domaine spécifique
sudo tail -f /var/log/apache2/monsite.com-*.log

# Vérifier les erreurs SSL/TLS
sudo grep -i ssl /var/log/apache2/error.log
```

## 🚀 Conseils de Performance

### Optimiser la configuration Apache

```bash
# Activer la compression
sudo a2enmod deflate

# Activer la mise en cache
sudo a2enmod expires
sudo a2enmod headers

# Recharger Apache
sudo systemctl reload apache2
```

### Surveiller l'utilisation des ressources

```bash
# Vérifier les processus Apache
ps aux | grep apache2

# Surveiller les ressources du serveur
htop
```

## 📞 Support et Débogage

### Vérifier les versions

```bash
apache2 -v
certbot --version
python3 --version
```

### Logs importants

```bash
# Logs généraux d'Apache
sudo tail -f /var/log/apache2/error.log

# Logs Let's Encrypt
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Logs système
sudo journalctl -u apache2 -f
```

### Problèmes courants et solutions

| Problème | Solution |
|----------|----------|
| "Permission denied" | Exécuter avec `sudo` |
| "Port already in use" | Vérifier avec `lsof -i :PORT` |
| "Domain validation failed" | Vérifier l'enregistrement DNS A |
| "Certificate expired" | Exécuter `sudo certbot renew` |
| "Site not accessible" | Vérifier le statut et les logs d'Apache |

## 🔧 Personnalisation

### Ajouter une configuration personnalisée

Vous pouvez modifier les fichiers de configuration Apache générés :

```bash
# Éditer la configuration du site
sudo nano /etc/apache2/sites-available/monsite.com.conf

# Ajouter des directives personnalisées, puis recharger
sudo systemctl reload apache2
```

### Paramètres spécifiques à l'environnement

Pour les environnements de développement, vous pourriez vouloir :

```bash
# Créer un site sans SSL
sudo python3 manage.py create dev.monsite.com 3000 --no-ssl

# Utiliser différents ports pour différents environnements
sudo python3 manage.py create staging.monsite.com 3001
sudo python3 manage.py create prod.monsite.com 3002
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à soumettre une Pull Request au [dépôt reverse-proxy](https://github.com/Noubissie237/reverse-proxy).

## 📞 Support

Si vous rencontrez des problèmes ou avez des questions :

1. Consultez la section dépannage ci-dessus
2. Examinez les logs pour les messages d'erreur
3. Ouvrez une issue sur [GitHub](https://github.com/Noubissie237/reverse-proxy/issues)

---

**💡 Conseil Pro :** Ajoutez cet alias à votre `.bashrc` pour une utilisation plus facile :
```bash
alias check_dns='sudo python3 /chemin/vers/check_dns.py'
alias vhost='sudo python3 /chemin/vers/manage.py'
```

Puis utilisez simplement :
```bash
check_dns monsite.com
vhost create monsite.com 8080
vhost list
vhost delete monsite.com
```

---

**⭐ Mettez une étoile à ce dépôt** s'il vous a aidé à gérer vos Virtual Hosts Apache plus efficacement !

</details>

<details>
<summary>English Version</summary>

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
- **Git** installed (`sudo apt install git`)
- **Python 3.9+** with pip
- **Sudo privileges**
- **DNS configured** (A record pointing to your server)
- **Ports 80 and 443 open** in firewall

## 📦 Installation

### 1. Clone the repository

```bash
# Clone the GitHub repository
git clone https://github.com/Noubissie237/reverse-proxy.git

# Navigate to the directory
cd reverse-proxy

# Make scripts executable
chmod +x setup_ssl.sh
chmod +x manage.py
chmod +x check_dns.py
```

### 2. Install Python dependencies

```bash
# Install required dependencies
pip3 install -r requirements.txt
```

This installs:
- `requests`: For HTTP requests
- `email-validator`: For email validation

### 3. Initial SSL configuration (one time only)

```bash
sudo ./setup_ssl.sh
```

This command:
- Installs Certbot (Let's Encrypt)
- Configures automatic certificate renewal
- Configures firewall if necessary

## 🎯 Usage

### 4. Check DNS Configuration (RECOMMENDED)

```bash
python3 check_dns.py <domain>
```

### 5. Create a new site

```bash
sudo python3 manage.py create <domain> <port>
```

**Example:**
```bash
sudo python3 manage.py create mysite.com 8080
```

The script will ask you:
1. Your email (for Let's Encrypt, first time only)
2. Whether you want to install SSL certificate (recommended: y)

### List all sites

```bash
python3 manage.py list
```

### View detailed site status

```bash
python3 manage.py status
```

Shows for each site:
- Apache status (enabled/disabled)
- Service status on port
- SSL status and days until expiration
- Creation date

### Check SSL certificates

```bash
python3 manage.py check-ssl
```

Shows:
- List of all SSL certificates
- Expiration date
- Days remaining
- Alerts if expiration < 30 days

### View statistics

```bash
python3 manage.py stats
```

Shows:
- Total number of sites
- Active vs inactive sites
- SSL/non-SSL distribution
- Port distribution

### Delete a site

```bash
sudo python3 manage.py delete <domain>
```

### Renew SSL certificates

```bash
sudo python3 manage.py renew-ssl
```

### Create a site without SSL

```bash
sudo python3 manage.py create <domain> <port> --no-ssl
```

## 📖 Practical Examples

### Example 1: E-commerce site

```bash
# Create an e-commerce site on port 3000
sudo python3 manage.py create shop.com 3000
```

**Result:**
- `http://shop.com` → redirects to `https://shop.com`
- `https://shop.com` → proxies to `localhost:3000`
- Automatic and valid SSL certificate

### Example 2: Backend API

```bash
# API on port 8080
sudo python3 check_dns.py api.myapp.com
sudo python3 manage.py create api.myapp.com 8080
```

### Example 3: React Application

```bash
# React app in development on port 3000
sudo python3 check_dns.py app.example.com
sudo python3 manage.py create app.example.com 3000
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
   sudo python3 check_dns.py newsite.com
   sudo python3 manage.py create newsite.com 8080
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
python3 manage.py list

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
sudo python3 manage.py create dev.mysite.com 3000 --no-ssl

# Use different ports for different environments
sudo python3 manage.py create staging.mysite.com 3001
sudo python3 manage.py create prod.mysite.com 3002
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
alias check_dns='sudo python3 /path/to/check_dns.py'
alias vhost='sudo python3 /path/to/manage.py'
```

Then simply use:
```bash
check_dns mysite.com
vhost create mysite.com 8080
vhost list
vhost delete mysite.com
```

---

**⭐ Star this repository** if it helped you manage your Apache Virtual Hosts more efficiently!

</details>