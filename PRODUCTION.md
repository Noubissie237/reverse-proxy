# 🚀 Guide de Déploiement en Production

Ce guide vous aide à déployer Apache VHost Manager en production de manière sécurisée.

## 📋 Prérequis

- Ubuntu/Debian Server 20.04+
- Apache2 installé et configuré
- Python 3.9+
- Accès root/sudo
- Nom de domaine pointant vers votre serveur (optionnel pour l'interface web)

---

## 🔒 Étape 1 : Configuration de sécurité

### 1.1 Copier le fichier de configuration

```bash
cp .env.example .env.production
```

### 1.2 Générer une clé secrète

```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

### 1.3 Éditer .env.production

```bash
nano .env.production
```

**Modifiez ces valeurs :**

```bash
SECRET_KEY=<votre_clé_générée_ci_dessus>
ADMIN_USERNAME=votre_username  # Changez "admin"
ADMIN_PASSWORD=VotreMotDePasseFort123!  # Mot de passe fort
VHOST_VERBOSE=0  # Mode silencieux (logs dans fichiers uniquement)
```

---

## 📦 Étape 2 : Installation

### 2.1 Cloner le projet (si pas déjà fait)

```bash
cd /opt
sudo git clone https://github.com/Noubissie237/reverse-proxy.git
cd reverse-proxy
```

### 2.2 Installer les dépendances

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # Serveur WSGI production
```

### 2.3 Créer les répertoires de logs

```bash
sudo mkdir -p /var/log/vhost-manager
sudo chown root:root /var/log/vhost-manager
```

---

## 🚀 Étape 3 : Démarrage

### Option A : Démarrage manuel (test)

```bash
./start-production.sh
```

Le script va :
- ✅ Vérifier la configuration
- ✅ Avertir si les identifiants par défaut sont utilisés
- ✅ Lancer Gunicorn avec 4 workers
- ✅ Mode silencieux (pas de logs console)

### Option B : Service systemd (recommandé)

#### 3.1 Installer le service

```bash
# Copier le fichier service
sudo cp vhost-manager-web.service /etc/systemd/system/

# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage
sudo systemctl enable vhost-manager-web

# Démarrer le service
sudo systemctl start vhost-manager-web
```

#### 3.2 Vérifier le statut

```bash
sudo systemctl status vhost-manager-web
```

#### 3.3 Voir les logs

```bash
# Logs du service
sudo journalctl -u vhost-manager-web -f

# Logs de l'application
sudo tail -f /var/log/vhost-manager/access.log
sudo tail -f /var/log/vhost-manager/error.log
```

---

## 🌐 Étape 4 : Reverse Proxy (HTTPS)

### 4.1 Créer un vhost pour l'interface web elle-même

```bash
# Créer un vhost avec SSL pour l'interface
sudo python3 manage.py create admin.votredomaine.com 5000
```

### 4.2 Configuration Apache manuelle (alternative)

```apache
<VirtualHost *:80>
    ServerName admin.votredomaine.com
    
    # Redirection HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
</VirtualHost>

<VirtualHost *:443>
    ServerName admin.votredomaine.com
    
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/admin.votredomaine.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/admin.votredomaine.com/privkey.pem
    
    # Proxy vers Gunicorn
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    # Headers de sécurité
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    
    # Logs
    ErrorLog ${APACHE_LOG_DIR}/admin-error.log
    CustomLog ${APACHE_LOG_DIR}/admin-access.log combined
</VirtualHost>
```

---

## 🔐 Étape 5 : Sécurité supplémentaire

### 5.1 Pare-feu

```bash
# N'exposer que les ports nécessaires
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# NE PAS exposer le port 5000 directement
# sudo ufw deny 5000/tcp

sudo ufw enable
```

### 5.2 Fail2ban (protection brute-force)

```bash
sudo apt install fail2ban

# Créer une jail pour l'interface
sudo nano /etc/fail2ban/jail.local
```

```ini
[vhost-manager]
enabled = true
port = http,https
filter = vhost-manager
logpath = /var/log/vhost-manager/access.log
maxretry = 5
bantime = 3600
```

### 5.3 Limiter l'accès par IP (optionnel)

Dans la config Apache :

```apache
<Location />
    # Autoriser uniquement certaines IPs
    Require ip 192.168.1.0/24
    Require ip 10.0.0.0/8
</Location>
```

---

## 📊 Étape 6 : Monitoring

### 6.1 Vérifier que le service tourne

```bash
sudo systemctl status vhost-manager-web
```

### 6.2 Surveiller les logs

```bash
# Logs en temps réel
sudo tail -f /var/log/vhost-manager/access.log

# Erreurs
sudo tail -f /var/log/vhost-manager/error.log

# Logs système
sudo journalctl -u vhost-manager-web -f
```

### 6.3 Tester l'interface

```bash
# Test local
curl http://localhost:5000

# Test externe (si reverse proxy configuré)
curl https://admin.votredomaine.com
```

---

## 🔄 Étape 7 : Mises à jour

### 7.1 Mettre à jour le code

```bash
cd /opt/reverse-proxy
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 7.2 Redémarrer le service

```bash
sudo systemctl restart vhost-manager-web
```

---

## 🐛 Dépannage

### Le service ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u vhost-manager-web -n 50

# Vérifier la configuration
sudo systemctl status vhost-manager-web

# Tester manuellement
cd /opt/reverse-proxy
source venv/bin/activate
./start-production.sh
```

### Erreur "Permission denied"

```bash
# Vérifier les permissions
sudo chown -R root:root /opt/reverse-proxy
sudo chmod +x start-production.sh
```

### Port 5000 déjà utilisé

```bash
# Trouver le processus
sudo lsof -i :5000

# Modifier le port dans .env.production
PORT=5001
```

---

## 📝 Checklist de déploiement

- [ ] Configuration .env.production créée et sécurisée
- [ ] SECRET_KEY changée
- [ ] ADMIN_PASSWORD changé
- [ ] VHOST_VERBOSE=0 (mode silencieux)
- [ ] Dépendances installées (gunicorn inclus)
- [ ] Service systemd configuré et activé
- [ ] Reverse proxy Apache configuré avec SSL
- [ ] Pare-feu configuré (ports 80, 443 ouverts, 5000 fermé)
- [ ] Fail2ban configuré (optionnel)
- [ ] Logs accessibles et surveillés
- [ ] Backup de la configuration planifié

---

## 🎯 Commandes utiles

```bash
# Démarrer le service
sudo systemctl start vhost-manager-web

# Arrêter le service
sudo systemctl stop vhost-manager-web

# Redémarrer le service
sudo systemctl restart vhost-manager-web

# Voir le statut
sudo systemctl status vhost-manager-web

# Voir les logs
sudo journalctl -u vhost-manager-web -f

# Recharger après modification du .service
sudo systemctl daemon-reload
sudo systemctl restart vhost-manager-web
```

---

## 🚀 Performances

### Configuration Gunicorn recommandée

Pour un serveur avec 4 CPU cores :

```bash
# Dans .env.production
WORKERS=9  # (2 x CPU cores) + 1
TIMEOUT=120
```

### Optimisation Apache

```apache
# /etc/apache2/mods-available/mpm_event.conf
<IfModule mpm_event_module>
    StartServers             4
    MinSpareThreads         25
    MaxSpareThreads         75
    ThreadLimit             64
    ThreadsPerChild         25
    MaxRequestWorkers      400
    MaxConnectionsPerChild   0
</IfModule>
```

---

**🎉 Votre interface web est maintenant en production !**

Accédez-y via : `https://admin.votredomaine.com`

---

**Support :** [GitHub Issues](https://github.com/Noubissie237/reverse-proxy/issues)
