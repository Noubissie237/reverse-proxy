# 🌐 Apache Virtual Host Manager

![Tests](https://github.com/Noubissie237/reverse-proxy/workflows/Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.5.0-orange)

[English](#english) | [Français](#français)

---

<a name="français"></a>
## 🇫🇷 Version Française

**Gestionnaire automatisé de Virtual Hosts Apache avec interface web moderne**

Gérez vos Virtual Hosts Apache en quelques clics grâce à une interface web intuitive. SSL/HTTPS automatique, monitoring en temps réel, et bien plus encore.

### ✨ Fonctionnalités

- 🖥️ **Interface Web Moderne** : Gérez tout depuis votre navigateur
- 📊 **Dashboard Intuitif** : Vue d'ensemble avec statistiques en temps réel
- 🌐 **Gestion Visuelle** : Créer, lister, supprimer des sites en quelques clics
- 🔒 **SSL Automatique** : Certificats Let's Encrypt gratuits et automatiques
- 📈 **Monitoring Live** : Statut Apache, ports, SSL avec auto-refresh
- 🔐 **Sécurisé** : Authentification, HTTPS forcé, en-têtes de sécurité
- 🎨 **Design Responsive** : Interface moderne avec TailwindCSS
- ⚡ **Certificats Wildcard** : Support `*.example.com` pour tous les sous-domaines
- 📝 **Logs Séparés** : Un fichier de log par domaine
- 🔄 **Renouvellement Auto** : Certificats SSL renouvelés automatiquement

### 📋 Prérequis

- **Serveur Linux** (Ubuntu/Debian 20.04+ recommandé)
- **Apache2** installé et configuré
- **Python 3.9+** avec pip
- **Privilèges sudo**
- **DNS configuré** (enregistrement A pointant vers votre serveur)
- **Ports 80 et 443 ouverts** dans le pare-feu

### 🚀 Installation

#### 1. Cloner le dépôt

```bash
git clone https://github.com/Noubissie237/reverse-proxy.git
cd reverse-proxy
```

#### 2. Installer les dépendances

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

#### 3. Configuration SSL initiale

```bash
# Rendre les scripts exécutables
chmod +x setup_ssl.sh start-web.sh start-production.sh

# Installer Certbot et configurer le renouvellement automatique
sudo ./setup_ssl.sh
```

### 🎯 Utilisation

#### Démarrer l'interface web

**Mode développement :**
```bash
./start-web.sh
```

**Mode production :**
```bash
# Configurer la sécurité
cp .env.example .env.production
nano .env.production  # Modifier SECRET_KEY et ADMIN_PASSWORD

# Lancer
./start-production.sh
```

#### Accéder à l'interface

1. **Ouvrir le navigateur** : `http://localhost:5000`
2. **Se connecter** :
   - Username : `admin`
   - Password : `admin` (⚠️ à changer en production !)

#### Créer un site

1. **Lancer votre application** (ex: sur le port 8080)
2. **Dans l'interface web** :
   - Cliquer sur **"Sites"** → **"Nouveau site"**
   - **Domaine** : `monsite.com`
   - **Port** : `8080`
   - **SSL** : ✅ Cocher pour activer HTTPS
   - Cliquer sur **"Créer le site"**
3. **Tester** : Ouvrir `https://monsite.com`

**Résultat :**
- ✅ `http://monsite.com` → redirige vers `https://monsite.com`
- ✅ `https://monsite.com` → proxy vers votre app sur `localhost:8080`
- ✅ Certificat SSL valide et automatique

#### Fonctionnalités de l'interface

| Page | Description |
|------|-------------|
| **Dashboard** | Vue d'ensemble : nombre de sites, alertes SSL, statistiques |
| **Sites** | Liste de tous vos sites avec statut (actif/inactif) |
| **Nouveau site** | Formulaire de création : domaine + port + SSL |
| **Monitoring** | Statut en temps réel : Apache, services, SSL (auto-refresh 30s) |
| **SSL Check** | Vérification des certificats et dates d'expiration |

### 📖 Exemples

#### Exemple 1 : Site e-commerce

```bash
# 1. Lancer votre app Node.js
npm start  # Écoute sur le port 3000

# 2. Ouvrir l'interface : http://localhost:5000
# 3. Créer le site :
#    - Domaine : boutique.com
#    - Port : 3000
#    - SSL : ✅
```

#### Exemple 2 : API Backend

```bash
# 1. Lancer votre API Python
python api.py  # Écoute sur le port 8080

# 2. Dans l'interface web :
#    - Domaine : api.monapp.com
#    - Port : 8080
#    - SSL : ✅
```

#### Exemple 3 : Certificat Wildcard

Pour gérer plusieurs sous-domaines avec un seul certificat :

```bash
# Via CLI (nécessite validation DNS manuelle)
sudo python3 manage.py install-wildcard-ssl '*.example.com'

# Puis créer les sites dans l'interface web :
# - api.example.com → port 8080
# - app.example.com → port 3000
# - admin.example.com → port 5000
```

📚 **Guide complet** : [WILDCARD_SSL_GUIDE.md](WILDCARD_SSL_GUIDE.md)

### 🔧 Configuration Avancée

#### Sécuriser l'interface web

```bash
# 1. Générer une clé secrète
python3 -c 'import secrets; print(secrets.token_hex(32))'

# 2. Modifier .env.production
nano .env.production
```

```bash
SECRET_KEY=<votre_clé_générée>
ADMIN_USERNAME=votre_admin
ADMIN_PASSWORD=MotDePasseFort123!
VHOST_VERBOSE=0  # Mode silencieux
```

#### Installer comme service systemd

```bash
# Copier le fichier service
sudo cp vhost-manager-web.service /etc/systemd/system/

# Activer et démarrer
sudo systemctl daemon-reload
sudo systemctl enable vhost-manager-web
sudo systemctl start vhost-manager-web

# Vérifier le statut
sudo systemctl status vhost-manager-web
```

#### Créer un reverse proxy pour l'interface

Pour accéder à l'interface via HTTPS :

```bash
# Via CLI
sudo python3 manage.py create admin.votredomaine.com 5000

# Puis accéder via : https://admin.votredomaine.com
```

### 🛠️ Dépannage

#### L'interface web ne démarre pas

```bash
# Vérifier les logs
sudo tail -f /var/log/vhost-manager/error.log

# Relancer
./start-web.sh
```

#### Erreur "ModuleNotFoundError: No module named 'flask'"

```bash
# Utiliser le script qui gère le venv automatiquement
./start-web.sh

# Ou activer le venv manuellement
source venv/bin/activate
python3 web/app.py
```

#### Site créé mais inaccessible

1. **Vérifier le DNS** :
   ```bash
   python3 check_dns.py monsite.com
   ```

2. **Vérifier que l'app tourne** :
   ```bash
   curl localhost:8080
   ```

3. **Voir les logs Apache** :
   ```bash
   sudo tail -f /var/log/apache2/monsite.com-error.log
   ```

4. **Vérifier dans l'interface** :
   - Monitoring → Voir le statut du service

#### Certificat SSL non créé

```bash
# Vérifier les logs Let's Encrypt
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Vérifier que le DNS pointe vers votre serveur
python3 check_dns.py monsite.com

# Vérifier les ports
sudo ufw status
```

### 📚 Documentation Complète

- 📖 [Guide de Production](PRODUCTION.md) - Déploiement en production
- 🌐 [Interface Web](web/README.md) - Documentation de l'interface
- 🔒 [Certificats Wildcard](WILDCARD_SSL_GUIDE.md) - Guide wildcard SSL
- 📦 [Package vhost_manager](vhost_manager/README.md) - Documentation du package

### 🔐 Sécurité

- ✅ **HTTPS forcé** : Redirection automatique HTTP → HTTPS
- ✅ **HSTS activé** : Protection contre les attaques de rétrogradation
- ✅ **En-têtes de sécurité** : X-Frame-Options, X-Content-Type-Options, etc.
- ✅ **Authentification** : Accès protégé à l'interface web
- ✅ **Certificats valides** : Let's Encrypt reconnu par tous les navigateurs

### 📞 Support

- 📖 **Documentation** : Voir les fichiers `.md` dans le projet
- 🐛 **Bugs** : [GitHub Issues](https://github.com/Noubissie237/reverse-proxy/issues)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/Noubissie237/reverse-proxy/discussions)

### 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

<a name="english"></a>
## 🇬🇧 English Version

**Automated Apache Virtual Host Manager with Modern Web Interface**

Manage your Apache Virtual Hosts with just a few clicks using an intuitive web interface. Automatic SSL/HTTPS, real-time monitoring, and much more.

### ✨ Features

- 🖥️ **Modern Web Interface**: Manage everything from your browser
- 📊 **Intuitive Dashboard**: Overview with real-time statistics
- 🌐 **Visual Management**: Create, list, delete sites with a few clicks
- 🔒 **Automatic SSL**: Free and automatic Let's Encrypt certificates
- 📈 **Live Monitoring**: Apache status, ports, SSL with auto-refresh
- 🔐 **Secure**: Authentication, forced HTTPS, security headers
- 🎨 **Responsive Design**: Modern interface with TailwindCSS
- ⚡ **Wildcard Certificates**: Support `*.example.com` for all subdomains
- 📝 **Separate Logs**: One log file per domain
- 🔄 **Auto Renewal**: SSL certificates renewed automatically

### 📋 Prerequisites

- **Linux Server** (Ubuntu/Debian 20.04+ recommended)
- **Apache2** installed and configured
- **Python 3.9+** with pip
- **Sudo privileges**
- **Configured DNS** (A record pointing to your server)
- **Ports 80 and 443 open** in firewall

### 🚀 Installation

#### 1. Clone the repository

```bash
git clone https://github.com/Noubissie237/reverse-proxy.git
cd reverse-proxy
```

#### 2. Install dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Initial SSL configuration

```bash
# Make scripts executable
chmod +x setup_ssl.sh start-web.sh start-production.sh

# Install Certbot and configure auto-renewal
sudo ./setup_ssl.sh
```

### 🎯 Usage

#### Start the web interface

**Development mode:**
```bash
./start-web.sh
```

**Production mode:**
```bash
# Configure security
cp .env.example .env.production
nano .env.production  # Edit SECRET_KEY and ADMIN_PASSWORD

# Launch
./start-production.sh
```

#### Access the interface

1. **Open browser**: `http://localhost:5000`
2. **Login**:
   - Username: `admin`
   - Password: `admin` (⚠️ change in production!)

#### Create a site

1. **Start your application** (e.g., on port 8080)
2. **In the web interface**:
   - Click **"Sites"** → **"New site"**
   - **Domain**: `mysite.com`
   - **Port**: `8080`
   - **SSL**: ✅ Check to enable HTTPS
   - Click **"Create site"**
3. **Test**: Open `https://mysite.com`

**Result:**
- ✅ `http://mysite.com` → redirects to `https://mysite.com`
- ✅ `https://mysite.com` → proxies to your app on `localhost:8080`
- ✅ Valid and automatic SSL certificate

#### Interface features

| Page | Description |
|------|-------------|
| **Dashboard** | Overview: number of sites, SSL alerts, statistics |
| **Sites** | List of all your sites with status (active/inactive) |
| **New site** | Creation form: domain + port + SSL |
| **Monitoring** | Real-time status: Apache, services, SSL (auto-refresh 30s) |
| **SSL Check** | Certificate verification and expiration dates |

### 📖 Examples

#### Example 1: E-commerce site

```bash
# 1. Start your Node.js app
npm start  # Listening on port 3000

# 2. Open interface: http://localhost:5000
# 3. Create site:
#    - Domain: shop.com
#    - Port: 3000
#    - SSL: ✅
```

#### Example 2: Backend API

```bash
# 1. Start your Python API
python api.py  # Listening on port 8080

# 2. In web interface:
#    - Domain: api.myapp.com
#    - Port: 8080
#    - SSL: ✅
```

#### Example 3: Wildcard Certificate

To manage multiple subdomains with a single certificate:

```bash
# Via CLI (requires manual DNS validation)
sudo python3 manage.py install-wildcard-ssl '*.example.com'

# Then create sites in web interface:
# - api.example.com → port 8080
# - app.example.com → port 3000
# - admin.example.com → port 5000
```

📚 **Complete guide**: [WILDCARD_SSL_GUIDE.md](WILDCARD_SSL_GUIDE.md)

### 🔧 Advanced Configuration

#### Secure the web interface

```bash
# 1. Generate secret key
python3 -c 'import secrets; print(secrets.token_hex(32))'

# 2. Edit .env.production
nano .env.production
```

```bash
SECRET_KEY=<your_generated_key>
ADMIN_USERNAME=your_admin
ADMIN_PASSWORD=StrongPassword123!
VHOST_VERBOSE=0  # Silent mode
```

#### Install as systemd service

```bash
# Copy service file
sudo cp vhost-manager-web.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable vhost-manager-web
sudo systemctl start vhost-manager-web

# Check status
sudo systemctl status vhost-manager-web
```

#### Create reverse proxy for the interface

To access the interface via HTTPS:

```bash
# Via CLI
sudo python3 manage.py create admin.yourdomain.com 5000

# Then access via: https://admin.yourdomain.com
```

### 🛠️ Troubleshooting

#### Web interface won't start

```bash
# Check logs
sudo tail -f /var/log/vhost-manager/error.log

# Restart
./start-web.sh
```

#### Error "ModuleNotFoundError: No module named 'flask'"

```bash
# Use the script that handles venv automatically
./start-web.sh

# Or activate venv manually
source venv/bin/activate
python3 web/app.py
```

#### Site created but inaccessible

1. **Check DNS**:
   ```bash
   python3 check_dns.py mysite.com
   ```

2. **Check app is running**:
   ```bash
   curl localhost:8080
   ```

3. **View Apache logs**:
   ```bash
   sudo tail -f /var/log/apache2/mysite.com-error.log
   ```

4. **Check in interface**:
   - Monitoring → View service status

#### SSL certificate not created

```bash
# Check Let's Encrypt logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Check DNS points to your server
python3 check_dns.py mysite.com

# Check ports
sudo ufw status
```

### 📚 Complete Documentation

- 📖 [Production Guide](PRODUCTION.md) - Production deployment
- 🌐 [Web Interface](web/README.md) - Interface documentation
- 🔒 [Wildcard Certificates](WILDCARD_SSL_GUIDE.md) - Wildcard SSL guide
- 📦 [vhost_manager Package](vhost_manager/README.md) - Package documentation

### 🔐 Security

- ✅ **Forced HTTPS**: Automatic HTTP → HTTPS redirection
- ✅ **HSTS enabled**: Protection against downgrade attacks
- ✅ **Security headers**: X-Frame-Options, X-Content-Type-Options, etc.
- ✅ **Authentication**: Protected access to web interface
- ✅ **Valid certificates**: Let's Encrypt recognized by all browsers

### 📞 Support

- 📖 **Documentation**: See `.md` files in the project
- 🐛 **Bugs**: [GitHub Issues](https://github.com/Noubissie237/reverse-proxy/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Noubissie237/reverse-proxy/discussions)

### 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**⭐ If this project is useful to you, don't hesitate to give it a star on GitHub! ⭐**

Made with ❤️ by [Noubissie237](https://github.com/Noubissie237)

</div>
