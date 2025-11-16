# Apache Virtual Host Manager

![Tests](https://github.com/Noubissie237/reverse-proxy/workflows/Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.5.0-orange)

**Gestionnaire automatisé de Virtual Hosts Apache avec interface web moderne**

**Automated Apache Virtual Host Manager with Modern Web Interface**

---

<details>
<summary><h2>🇫🇷 Version Française</h2></summary>

Gérez vos Virtual Hosts Apache en quelques clics grâce à une interface web intuitive. SSL/HTTPS automatique, monitoring en temps réel, et bien plus encore.

## Fonctionnalités

- **Interface Web Moderne** : Gérez tout depuis votre navigateur
- **Dashboard Intuitif** : Vue d'ensemble avec statistiques en temps réel
- **Gestion Visuelle** : Créer, lister, supprimer des sites en quelques clics
- **SSL Automatique** : Certificats Let's Encrypt gratuits et automatiques
- **Monitoring Live** : Statut Apache, ports, SSL avec auto-refresh
- **Sécurisé** : Authentification, HTTPS forcé, en-têtes de sécurité
- **Design Responsive** : Interface moderne avec TailwindCSS
- **Certificats Wildcard** : Support `*.example.com` pour tous les sous-domaines
- **Logs Séparés** : Un fichier de log par domaine
- **Renouvellement Auto** : Certificats SSL renouvelés automatiquement

## Prérequis

- **Serveur Linux** (Ubuntu/Debian 20.04+ recommandé)
- **Apache2** installé et configuré
- **Python 3.9+** avec pip
- **Privilèges sudo**
- **DNS configuré** (enregistrement A pointant vers votre serveur)
- **Ports 80 et 443 ouverts** dans le pare-feu

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Noubissie237/reverse-proxy.git
cd reverse-proxy
```

### 2. Installer les dépendances

```bash
# Créer un environnement virtuel
sudo apt install python3.10-venv
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration SSL initiale

```bash
# Rendre les scripts exécutables
chmod +x setup_ssl.sh start-production.sh

# Installer Certbot et configurer le renouvellement automatique
sudo ./setup_ssl.sh
```

## Configuration de l'interface web

### Étape 1 : Créer le fichier de configuration

```bash
cp .env.example .env.production
```

### Étape 2 : Générer une clé secrète

```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

**Copiez la clé générée**, vous en aurez besoin à l'étape suivante.

### Étape 3 : Modifier le fichier de configuration

```bash
nano .env.production
```

**Instructions pour utiliser nano :**

1. **Naviguer** : Utilisez les flèches du clavier pour vous déplacer
2. **Modifier** : Tapez directement pour modifier le texte
3. **Sauvegarder** : Appuyez sur `Ctrl + O`, puis `Entrée`
4. **Quitter** : Appuyez sur `Ctrl + X`

**Modifiez les lignes suivantes :**

```bash
SECRET_KEY=CHANGE_THIS_TO_A_RANDOM_SECRET_KEY
# Remplacez par la clé générée à l'étape 2

ADMIN_USERNAME=admin
# Remplacez "admin" par votre nom d'utilisateur

ADMIN_PASSWORD=CHANGE_THIS_PASSWORD
# Remplacez par un mot de passe fort (minimum 12 caractères)
```

**Exemple de configuration sécurisée :**

```bash
SECRET_KEY=a8f5f167f44f4964e6c998dee827110c47f1f1c6f5e5f8e5f5e5f5e5f5e5f5e5
ADMIN_USERNAME=admin_prod
ADMIN_PASSWORD=MonMotDePasse2024!Securise
VHOST_VERBOSE=0
```

**Sauvegardez et quittez** : `Ctrl + O`, `Entrée`, puis `Ctrl + X`

## Démarrage de l'interface web

### Lancer l'interface en production

```bash
./start-production.sh
```

Le script va :
- Vérifier votre configuration
- Installer Gunicorn si nécessaire
- Démarrer l'interface avec 4 workers
- Afficher l'URL d'accès

**Sortie attendue :**

```
═══════════════════════════════════════════════
  Apache VHost Manager - Production Mode
═══════════════════════════════════════════════

✓ Chargement de .env.production
✓ Environnement virtuel activé
✓ Privilèges sudo: OK

Configuration
═══════════════════════════════════════════════
  Mode:          PRODUCTION
  Workers:       4
  Bind:          0.0.0.0:5000
  Timeout:       120s
  Verbose:       0
═══════════════════════════════════════════════

🚀 Démarrage de Gunicorn...
```

### Accéder à l'interface

1. **Ouvrir le navigateur** : `http://localhost:5000`
2. **Se connecter** avec les identifiants configurés dans `.env.production`

**Note :** Pour accéder depuis un autre appareil sur le réseau, utilisez l'IP du serveur :
```
http://192.168.1.X:5000
```

## Utilisation de l'interface

### Créer un site

1. **Prérequis** : Votre application doit être lancée et écouter sur un port (ex: 8080)

2. **Dans l'interface web** :
   - Cliquer sur **"Sites"** dans le menu
   - Cliquer sur **"Nouveau site"**
   - Remplir le formulaire :
     - **Domaine** : `monsite.com`
     - **Port** : `8080`
     - **SSL** : Cocher pour activer HTTPS
   - Cliquer sur **"Créer le site"**

3. **Vérifier** : Ouvrir `https://monsite.com` dans votre navigateur

**Résultat :**
- `http://monsite.com` redirige automatiquement vers `https://monsite.com`
- `https://monsite.com` affiche votre application
- Certificat SSL valide et automatique

### Fonctionnalités de l'interface

| Page | Description |
|------|-------------|
| **Dashboard** | Vue d'ensemble : nombre de sites, alertes SSL, statistiques |
| **Sites** | Liste de tous vos sites avec statut (actif/inactif) |
| **Nouveau site** | Formulaire de création : domaine + port + SSL |
| **Monitoring** | Statut en temps réel : Apache, services, SSL (auto-refresh 30s) |
| **SSL Check** | Vérification des certificats et dates d'expiration |

## Exemples d'utilisation

### Exemple 1 : Site e-commerce

```bash
# 1. Lancer votre application Node.js
npm start  # Écoute sur le port 3000
```

Dans l'interface web :
- Domaine : `boutique.com`
- Port : `3000`
- SSL : ✓ Activé

### Exemple 2 : API Backend

```bash
# 1. Lancer votre API Python
python api.py  # Écoute sur le port 8080
```

Dans l'interface web :
- Domaine : `api.monapp.com`
- Port : `8080`
- SSL : ✓ Activé

### Exemple 3 : Certificat Wildcard

Pour gérer plusieurs sous-domaines avec un seul certificat :

```bash
# Via ligne de commande (nécessite validation DNS manuelle)
sudo python3 manage.py install-wildcard-ssl '*.example.com'
```

Puis créer les sites dans l'interface web :
- `api.example.com` → port 8080
- `app.example.com` → port 3000
- `admin.example.com` → port 5000

**Guide complet** : [WILDCARD_SSL_GUIDE.md](WILDCARD_SSL_GUIDE.md)

## Installation comme service systemd

Pour que l'interface démarre automatiquement au démarrage du serveur :

### 1. Copier le fichier service

```bash
sudo cp vhost-manager-web.service /etc/systemd/system/
```

### 2. Activer et démarrer le service

```bash
sudo systemctl daemon-reload
sudo systemctl enable vhost-manager-web
sudo systemctl start vhost-manager-web
```

### 3. Vérifier le statut

```bash
sudo systemctl status vhost-manager-web
```

### 4. Commandes utiles

```bash
# Démarrer
sudo systemctl start vhost-manager-web

# Arrêter
sudo systemctl stop vhost-manager-web

# Redémarrer
sudo systemctl restart vhost-manager-web

# Voir les logs
sudo journalctl -u vhost-manager-web -f
```

## Sécuriser l'interface avec HTTPS

Pour accéder à l'interface via HTTPS (recommandé en production) :

```bash
# Créer un reverse proxy pour l'interface elle-même
sudo python3 manage.py create admin.votredomaine.com 5000
```

Ensuite, accédez à l'interface via : `https://admin.votredomaine.com`

## Dépannage

### L'interface ne démarre pas

```bash
# Vérifier les logs
sudo tail -f /var/log/vhost-manager/error.log

# Vérifier que le port 5000 n'est pas utilisé
sudo lsof -i :5000

# Relancer
./start-production.sh
```

### Erreur "ModuleNotFoundError: No module named 'flask'"

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Relancer
./start-production.sh
```

### Site créé mais inaccessible

**1. Vérifier le DNS :**
```bash
python3 check_dns.py monsite.com
```

**2. Vérifier que l'application tourne :**
```bash
curl localhost:8080
```

**3. Voir les logs Apache :**
```bash
sudo tail -f /var/log/apache2/monsite.com-error.log
```

**4. Vérifier dans l'interface :**
- Menu **Monitoring** → Voir le statut du service

### Certificat SSL non créé

**1. Vérifier les logs Let's Encrypt :**
```bash
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

**2. Vérifier que le DNS pointe vers votre serveur :**
```bash
python3 check_dns.py monsite.com
```

**3. Vérifier que les ports sont ouverts :**
```bash
sudo ufw status
```

**4. Vérifier dans l'interface :**
- Menu **SSL Check** → Voir les détails des certificats

## Configuration du pare-feu

```bash
# Autoriser Apache (ports 80 et 443)
sudo ufw allow 'Apache Full'

# Autoriser SSH
sudo ufw allow ssh

# Autoriser l'interface web (si accès externe)
sudo ufw allow 5000/tcp

# Activer le pare-feu
sudo ufw enable

# Vérifier le statut
sudo ufw status
```

## Documentation complète

- [Guide de Production](PRODUCTION.md) - Déploiement en production
- [Interface Web](web/README.md) - Documentation de l'interface
- [Certificats Wildcard](WILDCARD_SSL_GUIDE.md) - Guide wildcard SSL
- [Dépannage SSL](SSL_TROUBLESHOOTING.md) - Résolution des problèmes SSL
- [Package vhost_manager](vhost_manager/README.md) - Documentation du package

## Sécurité

- **HTTPS forcé** : Redirection automatique HTTP → HTTPS
- **HSTS activé** : Protection contre les attaques de rétrogradation
- **En-têtes de sécurité** : X-Frame-Options, X-Content-Type-Options, etc.
- **Authentification** : Accès protégé à l'interface web
- **Certificats valides** : Let's Encrypt reconnu par tous les navigateurs
- **Mode production** : Logs silencieux, debug désactivé

## Support

- **Documentation** : Voir les fichiers `.md` dans le projet
- **Bugs** : [GitHub Issues](https://github.com/Noubissie237/reverse-proxy/issues)
- **Discussions** : [GitHub Discussions](https://github.com/Noubissie237/reverse-proxy/discussions)

## Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

</details>

---

<details>
<summary><h2>🇬🇧 English Version</h2></summary>

Manage your Apache Virtual Hosts with just a few clicks using an intuitive web interface. Automatic SSL/HTTPS, real-time monitoring, and much more.

## Features

- **Modern Web Interface**: Manage everything from your browser
- **Intuitive Dashboard**: Overview with real-time statistics
- **Visual Management**: Create, list, delete sites with a few clicks
- **Automatic SSL**: Free and automatic Let's Encrypt certificates
- **Live Monitoring**: Apache status, ports, SSL with auto-refresh
- **Secure**: Authentication, forced HTTPS, security headers
- **Responsive Design**: Modern interface with TailwindCSS
- **Wildcard Certificates**: Support `*.example.com` for all subdomains
- **Separate Logs**: One log file per domain
- **Auto Renewal**: SSL certificates renewed automatically

## Prerequisites

- **Linux Server** (Ubuntu/Debian 20.04+ recommended)
- **Apache2** installed and configured
- **Python 3.9+** with pip
- **Sudo privileges**
- **Configured DNS** (A record pointing to your server)
- **Ports 80 and 443 open** in firewall

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Noubissie237/reverse-proxy.git
cd reverse-proxy
```

### 2. Install dependencies

```bash
# Create virtual environment
sudo apt install python3.10-venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initial SSL configuration

```bash
# Make scripts executable
chmod +x setup_ssl.sh start-production.sh

# Install Certbot and configure auto-renewal
sudo ./setup_ssl.sh
```

## Web Interface Configuration

### Step 1: Create configuration file

```bash
cp .env.example .env.production
```

### Step 2: Generate secret key

```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

**Copy the generated key**, you will need it in the next step.

### Step 3: Edit configuration file

```bash
nano .env.production
```

**Instructions for using nano:**

1. **Navigate**: Use arrow keys to move around
2. **Edit**: Type directly to modify text
3. **Save**: Press `Ctrl + O`, then `Enter`
4. **Exit**: Press `Ctrl + X`

**Modify the following lines:**

```bash
SECRET_KEY=CHANGE_THIS_TO_A_RANDOM_SECRET_KEY
# Replace with the key generated in step 2

ADMIN_USERNAME=admin
# Replace "admin" with your username

ADMIN_PASSWORD=CHANGE_THIS_PASSWORD
# Replace with a strong password (minimum 12 characters)
```

**Example of secure configuration:**

```bash
SECRET_KEY=a8f5f167f44f4964e6c998dee827110c47f1f1c6f5e5f8e5f5e5f5e5f5e5f5e5
ADMIN_USERNAME=admin_prod
ADMIN_PASSWORD=MySecurePassword2024!
VHOST_VERBOSE=0
```

**Save and exit**: `Ctrl + O`, `Enter`, then `Ctrl + X`

## Starting the Web Interface

### Launch interface in production

```bash
./start-production.sh
```

The script will:
- Check your configuration
- Install Gunicorn if necessary
- Start the interface with 4 workers
- Display the access URL

**Expected output:**

```
═══════════════════════════════════════════════
  Apache VHost Manager - Production Mode
═══════════════════════════════════════════════

✓ Loading .env.production
✓ Virtual environment activated
✓ Sudo privileges: OK

Configuration
═══════════════════════════════════════════════
  Mode:          PRODUCTION
  Workers:       4
  Bind:          0.0.0.0:5000
  Timeout:       120s
  Verbose:       0
═══════════════════════════════════════════════

🚀 Starting Gunicorn...
```

### Access the interface

1. **Open browser**: `http://localhost:5000`
2. **Login** with credentials configured in `.env.production`

**Note:** To access from another device on the network, use the server IP:
```
http://192.168.1.X:5000
```

## Using the Interface

### Create a site

1. **Prerequisites**: Your application must be running and listening on a port (e.g., 8080)

2. **In the web interface**:
   - Click **"Sites"** in the menu
   - Click **"New site"**
   - Fill in the form:
     - **Domain**: `mysite.com`
     - **Port**: `8080`
     - **SSL**: Check to enable HTTPS
   - Click **"Create site"**

3. **Verify**: Open `https://mysite.com` in your browser

**Result:**
- `http://mysite.com` automatically redirects to `https://mysite.com`
- `https://mysite.com` displays your application
- Valid and automatic SSL certificate

### Interface features

| Page | Description |
|------|-------------|
| **Dashboard** | Overview: number of sites, SSL alerts, statistics |
| **Sites** | List of all your sites with status (active/inactive) |
| **New site** | Creation form: domain + port + SSL |
| **Monitoring** | Real-time status: Apache, services, SSL (auto-refresh 30s) |
| **SSL Check** | Certificate verification and expiration dates |

## Usage Examples

### Example 1: E-commerce site

```bash
# 1. Start your Node.js application
npm start  # Listening on port 3000
```

In the web interface:
- Domain: `shop.com`
- Port: `3000`
- SSL: ✓ Enabled

### Example 2: Backend API

```bash
# 1. Start your Python API
python api.py  # Listening on port 8080
```

In the web interface:
- Domain: `api.myapp.com`
- Port: `8080`
- SSL: ✓ Enabled

### Example 3: Wildcard Certificate

To manage multiple subdomains with a single certificate:

```bash
# Via command line (requires manual DNS validation)
sudo python3 manage.py install-wildcard-ssl '*.example.com'
```

Then create sites in the web interface:
- `api.example.com` → port 8080
- `app.example.com` → port 3000
- `admin.example.com` → port 5000

**Complete guide**: [WILDCARD_SSL_GUIDE.md](WILDCARD_SSL_GUIDE.md)

## Install as systemd service

To have the interface start automatically on server boot:

### 1. Copy service file

```bash
sudo cp vhost-manager-web.service /etc/systemd/system/
```

### 2. Enable and start service

```bash
sudo systemctl daemon-reload
sudo systemctl enable vhost-manager-web
sudo systemctl start vhost-manager-web
```

### 3. Check status

```bash
sudo systemctl status vhost-manager-web
```

### 4. Useful commands

```bash
# Start
sudo systemctl start vhost-manager-web

# Stop
sudo systemctl stop vhost-manager-web

# Restart
sudo systemctl restart vhost-manager-web

# View logs
sudo journalctl -u vhost-manager-web -f
```

## Secure interface with HTTPS

To access the interface via HTTPS (recommended in production):

```bash
# Create a reverse proxy for the interface itself
sudo python3 manage.py create admin.yourdomain.com 5000
```

Then access the interface via: `https://admin.yourdomain.com`

## Troubleshooting

### Interface won't start

```bash
# Check logs
sudo tail -f /var/log/vhost-manager/error.log

# Check if port 5000 is not in use
sudo lsof -i :5000

# Restart
./start-production.sh
```

### Error "ModuleNotFoundError: No module named 'flask'"

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Restart
./start-production.sh
```

### Site created but inaccessible

**1. Check DNS:**
```bash
python3 check_dns.py mysite.com
```

**2. Check application is running:**
```bash
curl localhost:8080
```

**3. View Apache logs:**
```bash
sudo tail -f /var/log/apache2/mysite.com-error.log
```

**4. Check in interface:**
- **Monitoring** menu → View service status

### SSL certificate not created

**1. Check Let's Encrypt logs:**
```bash
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

**2. Check DNS points to your server:**
```bash
python3 check_dns.py mysite.com
```

**3. Check ports are open:**
```bash
sudo ufw status
```

**4. Check in interface:**
- **SSL Check** menu → View certificate details

## Firewall Configuration

```bash
# Allow Apache (ports 80 and 443)
sudo ufw allow 'Apache Full'

# Allow SSH
sudo ufw allow ssh

# Allow web interface (if external access)
sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Complete Documentation

- [Production Guide](PRODUCTION.md) - Production deployment
- [Web Interface](web/README.md) - Interface documentation
- [Wildcard Certificates](WILDCARD_SSL_GUIDE.md) - Wildcard SSL guide
- [SSL Troubleshooting](SSL_TROUBLESHOOTING.md) - SSL issue resolution
- [vhost_manager Package](vhost_manager/README.md) - Package documentation

## Security

- **Forced HTTPS**: Automatic HTTP → HTTPS redirection
- **HSTS enabled**: Protection against downgrade attacks
- **Security headers**: X-Frame-Options, X-Content-Type-Options, etc.
- **Authentication**: Protected access to web interface
- **Valid certificates**: Let's Encrypt recognized by all browsers
- **Production mode**: Silent logs, debug disabled

## Support

- **Documentation**: See `.md` files in the project
- **Bugs**: [GitHub Issues](https://github.com/Noubissie237/reverse-proxy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Noubissie237/reverse-proxy/discussions)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

</details>

---

<div align="center">

**If this project is useful to you, don't hesitate to give it a star on GitHub!**

Made with ❤️ by [Noubissie237](https://github.com/Noubissie237)

</div>
