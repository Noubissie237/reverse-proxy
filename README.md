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
- **Apache2** installé et configuré sur l'hôte
- **Docker** et **Docker Compose** installés
- **Privilèges sudo**
- **DNS configuré** (enregistrement A pointant vers votre serveur)
- **Ports 80, 443 et 5000 ouverts** dans le pare-feu

## Installation Docker

### Étape 1 : Vérifiez que vous avez Docker et Docker Compose installés

```bash
docker --version
docker compose --version
```

### Étape 2 : Cloner le projet

```bash
git clone https://github.com/Noubissie237/reverse-proxy.git
cd reverse-proxy
```

### Étape 3 : Configurer l'application

```bash
# Copier le fichier de configuration
cp .env.example .env.production

# Générer une clé secrète
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

**Copiez la clé générée**, puis modifiez `.env.production` :

```bash
nano .env.production
```

**Modifiez ces lignes :**

```bash
SECRET_KEY=votre_cle_generee_ici
ADMIN_USERNAME=votre_username
ADMIN_PASSWORD=VotreMotDePasseSecurise123!
```

**Exemple de configuration sécurisée :**

```bash
SECRET_KEY=a8f5f167f44f4964e6c998dee827110c47f1f1c6f5e5f8e5f5e5f5e5f5e5f5e5
ADMIN_USERNAME=admin_prod
ADMIN_PASSWORD=MonMotDePasse2024!Securise
VHOST_VERBOSE=0
HOST=0.0.0.0
PORT=5000
```

**Sauvegardez** : `Ctrl + O`, `Entrée`, puis `Ctrl + X`

### Étape 4 : Installer Certbot sur l'hôte

```bash
# Rendre le script exécutable
chmod +x setup_ssl.sh

# Installer Certbot et configurer le renouvellement automatique
sudo ./setup_ssl.sh
```

### Étape 5 : Démarrer l'application

```bash
# Rendre le script exécutable
chmod +x docker-start.sh

# Lancer l'application
./docker-start.sh
```

Le script va :
- ✅ Vérifier Docker et Docker Compose
- ✅ Vérifier la configuration de sécurité
- ✅ Construire l'image Docker
- ✅ Démarrer le conteneur en arrière-plan
- ✅ Afficher les informations d'accès

**Sortie attendue :**

```
═══════════════════════════════════════════════
  Apache VHost Manager - Docker Mode
═══════════════════════════════════════════════

✅ Configuration vérifiée

═══════════════════════════════════════════════
  Construction de l'image Docker
═══════════════════════════════════════════════

✅ Application démarrée avec succès !

═══════════════════════════════════════════════
  Informations d'accès
═══════════════════════════════════════════════
  URL:           http://localhost:5000
  Username:      admin_prod
  Logs:          docker-compose logs -f
  Status:        docker-compose ps
  Arrêter:       docker-compose stop
  Redémarrer:    docker-compose restart
  Supprimer:     docker-compose down
═══════════════════════════════════════════════
```

### Accéder à l'interface

1. **Ouvrir le navigateur** : `http://votre-serveur:5000`
2. **Se connecter** avec les identifiants configurés dans `.env.production`

## Gestion du conteneur

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Voir le statut
docker-compose ps

# Arrêter le conteneur
docker-compose stop

# Démarrer le conteneur
docker-compose start

# Redémarrer le conteneur
docker-compose restart

# Arrêter et supprimer le conteneur
docker-compose down

# Mettre à jour l'application
git pull
docker-compose up -d --build
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

## Sécuriser l'interface avec HTTPS

Pour accéder à l'interface via HTTPS (recommandé en production) :

```bash
# Accéder au conteneur
docker-compose exec vhost-manager bash

# Créer un reverse proxy pour l'interface elle-même
sudo python3 manage.py create admin.votredomaine.com 5000
```

Ensuite, accédez à l'interface via : `https://admin.votredomaine.com`

## Dépannage

### Le conteneur ne démarre pas

```bash
# Vérifier les logs
docker-compose logs -f

# Vérifier l'état
docker-compose ps

# Reconstruire complètement
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Erreur "port already in use"

```bash
# Vérifier quel processus utilise le port 5000
sudo lsof -i :5000

# Arrêter le processus ou changer le port dans .env.production
```

### Problèmes de permissions Apache

```bash
# Vérifier les permissions des répertoires Apache
ls -la /etc/apache2/sites-available
ls -la /etc/letsencrypt

# Si nécessaire, ajuster les permissions
sudo chmod -R 755 /etc/apache2/sites-available
sudo chmod -R 755 /etc/letsencrypt
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
- **Apache2** installed and configured on host
- **Docker** and **Docker Compose** installed
- **Sudo privileges**
- **Configured DNS** (A record pointing to your server)
- **Ports 80, 443 and 5000 open** in firewall

## Docker Installation

### Step 1: Check Docker Installation

```bash
# Verify installation
docker --version
docker compose --version
```

### Step 2: Clone the project

```bash
git clone https://github.com/Noubissie237/reverse-proxy.git
cd reverse-proxy
```

### Step 3: Configure the application

```bash
# Copy configuration file
cp .env.example .env.production

# Generate a secret key
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

**Copy the generated key**, then edit `.env.production`:

```bash
nano .env.production
```

**Modify these lines:**

```bash
SECRET_KEY=your_generated_key_here
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=YourSecurePassword123!
```

**Example of secure configuration:**

```bash
SECRET_KEY=a8f5f167f44f4964e6c998dee827110c47f1f1c6f5e5f8e5f5e5f5e5f5e5f5e5
ADMIN_USERNAME=admin_prod
ADMIN_PASSWORD=MySecurePassword2024!
VHOST_VERBOSE=0
HOST=0.0.0.0
PORT=5000
```

**Save**: `Ctrl + O`, `Enter`, then `Ctrl + X`

### Step 4: Install Certbot on host

```bash
# Make script executable
chmod +x setup_ssl.sh

# Install Certbot and configure auto-renewal
sudo ./setup_ssl.sh
```

### Step 5: Start the application

```bash
# Make script executable
chmod +x docker-start.sh

# Launch the application
./docker-start.sh
```

The script will:
- ✅ Check Docker and Docker Compose
- ✅ Verify security configuration
- ✅ Build Docker image
- ✅ Start container in background
- ✅ Display access information

**Expected output:**

```
═══════════════════════════════════════════════
  Apache VHost Manager - Docker Mode
═══════════════════════════════════════════════

✅ Configuration verified

═══════════════════════════════════════════════
  Building Docker image
═══════════════════════════════════════════════

✅ Application started successfully!

═══════════════════════════════════════════════
  Access Information
═══════════════════════════════════════════════
  URL:           http://localhost:5000
  Username:      admin_prod
  Logs:          docker-compose logs -f
  Status:        docker-compose ps
  Stop:          docker-compose stop
  Restart:       docker-compose restart
  Remove:        docker-compose down
═══════════════════════════════════════════════
```

### Access the interface

1. **Open browser**: `http://your-server:5000`
2. **Login** with credentials configured in `.env.production`

## Container Management

```bash
# View logs in real-time
docker-compose logs -f

# Check status
docker-compose ps

# Stop container
docker-compose stop

# Start container
docker-compose start

# Restart container
docker-compose restart

# Stop and remove container
docker-compose down

# Update application
git pull
docker-compose up -d --build
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

## Secure interface with HTTPS

To access the interface via HTTPS (recommended in production):

```bash
# Access the container
docker-compose exec vhost-manager bash

# Create a reverse proxy for the interface itself
sudo python3 manage.py create admin.yourdomain.com 5000
```

Then access the interface via: `https://admin.yourdomain.com`

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs -f

# Check status
docker-compose ps

# Rebuild completely
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Error "port already in use"

```bash
# Check which process is using port 5000
sudo lsof -i :5000

# Stop the process or change port in .env.production
```

### Apache permission issues

```bash
# Check Apache directories permissions
ls -la /etc/apache2/sites-available
ls -la /etc/letsencrypt

# If needed, adjust permissions
sudo chmod -R 755 /etc/apache2/sites-available
sudo chmod -R 755 /etc/letsencrypt
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
