# Installation Rapide - Apache VHost Manager (Docker)

## Prérequis

- ✅ Serveur Linux (Ubuntu/Debian)
- ✅ Apache2 installé et configuré
- ✅ Docker et Docker Compose installés
- ✅ Privilèges sudo
- ✅ Ports 80, 443 et 5000 ouverts

## Installation en 5 étapes

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/Noubissie237/reverse-proxy.git
cd reverse-proxy
```

### 2️⃣ Configurer les identifiants

```bash
# Copier le fichier d'exemple
cp .env.example .env.production

# Générer une clé secrète
python3 -c 'import secrets; print(secrets.token_hex(32))'

# Éditer le fichier .env.production
nano .env.production
```

Modifiez :
- `SECRET_KEY=` (utilisez la clé générée)
- `ADMIN_USERNAME=` (votre nom d'utilisateur)
- `ADMIN_PASSWORD=` (un mot de passe fort)

### 3️⃣ Installer l'Apache Agent

```bash
# Rendre le script exécutable
chmod +x install-apache-agent.sh

# Installer l'agent
sudo ./install-apache-agent.sh
```

L'agent va :
- ✅ S'installer dans `/opt/apache-vhost-manager/`
- ✅ Créer un service systemd
- ✅ Démarrer automatiquement
- ✅ Créer le socket `/var/run/apache-agent.sock`

### 4️⃣ Démarrer l'application

```bash
# Rendre le script exécutable
chmod +x docker-start.sh

# Lancer l'application
./docker-start.sh
```

### 5️⃣ Accéder à l'interface

Ouvrez votre navigateur : **http://votre-serveur:5000**

Connectez-vous avec les identifiants de `.env.production`

## Vérifications

### Vérifier que tout fonctionne

```bash
# Apache Agent
sudo systemctl status apache-agent
ls -la /var/run/apache-agent.sock

# Conteneur Docker
docker compose ps
docker compose logs -f

# Apache
sudo systemctl status apache2
```

### Tous les services doivent être actifs ✅

- Apache : `active (running)`
- Apache Agent : `active (running)`
- Conteneur : `Up`

## Commandes utiles

### Gestion du conteneur

```bash
# Voir les logs
docker compose logs -f

# Redémarrer
docker compose restart

# Arrêter
docker compose stop

# Supprimer
docker compose down
```

### Gestion de l'Apache Agent

```bash
# Statut
sudo systemctl status apache-agent

# Logs
sudo journalctl -u apache-agent -f

# Redémarrer
sudo systemctl restart apache-agent

# Arrêter
sudo systemctl stop apache-agent
```

### Gestion d'Apache

```bash
# Statut
sudo systemctl status apache2

# Redémarrer
sudo systemctl restart apache2

# Tester la configuration
sudo apache2ctl configtest
```

## Dépannage

### L'Apache Agent ne démarre pas

```bash
# Voir les erreurs
sudo journalctl -u apache-agent -n 50

# Supprimer le socket s'il existe en tant que répertoire
sudo rm -rf /var/run/apache-agent.sock

# Redémarrer
sudo systemctl restart apache-agent
```

### Le conteneur ne peut pas créer de sites

```bash
# Vérifier que l'agent fonctionne
sudo systemctl status apache-agent

# Vérifier le socket
ls -la /var/run/apache-agent.sock

# Vérifier les permissions du fichier JSON
sudo chmod 666 /etc/vhost_manager.json

# Redémarrer le conteneur
docker compose restart
```

### Apache ne démarre pas

```bash
# Voir les erreurs
sudo journalctl -u apache2 -n 50

# Tester la configuration
sudo apache2ctl configtest

# Activer les modules nécessaires
sudo a2enmod proxy proxy_http rewrite ssl headers

# Redémarrer Apache
sudo systemctl restart apache2
```

### SSL ne s'installe pas

```bash
# Vérifier que le DNS pointe vers le serveur
dig +short votre-domaine.com

# Vérifier que les ports sont ouverts
sudo netstat -tulpn | grep -E ':(80|443)'

# Désactiver les sites avec erreurs
sudo a2dissite site-problematique.conf
sudo systemctl reload apache2

# Réessayer
```

## Architecture

```
┌─────────────────────────────────────────────┐
│              Serveur (Hôte)                 │
│                                             │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │   Apache     │      │  Apache Agent   │ │
│  │  (Port 80)   │◄─────│  (Service)      │ │
│  │  (Port 443)  │      │                 │ │
│  └──────────────┘      └────────┬────────┘ │
│                                 │          │
│                        Socket Unix         │
│                                 │          │
│  ┌──────────────────────────────┼────────┐ │
│  │    Conteneur Docker          │        │ │
│  │                               │        │ │
│  │  ┌────────────────────────────▼─────┐ │ │
│  │  │  VHost Manager (Flask:5000)     │ │ │
│  │  └─────────────────────────────────┘ │ │
│  └──────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## Support

- 📖 Documentation complète : `README.md`
- 🔧 Guide Apache Agent : `DOCKER_APACHE_AGENT.md`
- 🔒 Guide SSL : `SSL_TROUBLESHOOTING.md`
- 🌐 GitHub : https://github.com/Noubissie237/reverse-proxy
