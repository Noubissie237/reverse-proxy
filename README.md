# 🌐 Apache Virtual Host Manager

![Tests](https://github.com/Noubissie237/reverse-proxy/workflows/Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.5.0-orange)

**Gestionnaire automatisé de Virtual Hosts Apache avec interface web moderne**

Automatisez la création et la gestion de Virtual Hosts Apache avec SSL/HTTPS automatique, interface web intuitive et monitoring en temps réel.

---

## ✨ Fonctionnalités

### 🖥️ Interface Web
- 📊 **Dashboard moderne** : Vue d'ensemble avec statistiques en temps réel
- 🌐 **Gestion visuelle** : Créer, lister, supprimer des sites via navigateur
- 📈 **Monitoring live** : Statut Apache, ports, SSL avec auto-refresh
- 🔒 **Vérification SSL** : Suivi des certificats et alertes d'expiration
- 🔐 **Authentification** : Accès sécurisé par login/password
- 🎨 **Design responsive** : Interface moderne avec TailwindCSS

### 🛠️ Ligne de commande (CLI)
- ✅ **Création automatisée** de Virtual Hosts Apache
- ✅ **SSL/HTTPS automatique** avec Let's Encrypt (certificats gratuits)
- ✅ **Certificats Wildcard** (`*.example.com`) pour tous les sous-domaines
- ✅ **Redirection automatique** HTTP → HTTPS
- ✅ **Proxy inverse** vers n'importe quel port local
- ✅ **Gestion complète** : créer, supprimer, lister, monitorer
- ✅ **Logs séparés** par domaine
- ✅ **Renouvellement automatique** des certificats SSL
- ✅ **En-têtes de sécurité** inclus
- ✅ **Architecture modulaire** : Code organisé et maintenable

---

## 📋 Prérequis

- **Serveur Linux** (Ubuntu/Debian 20.04+ recommandé)
- **Apache2** installé et configuré
- **Git** installé (`sudo apt install git`)
- **Python 3.9+** avec pip
- **Privilèges sudo**
- **DNS configuré** (enregistrement A pointant vers votre serveur)
- **Ports 80 et 443 ouverts** dans le pare-feu

---

## 🚀 Installation Rapide

### 1. Cloner le dépôt

```bash
# Cloner le dépôt GitHub
git clone https://github.com/Noubissie237/reverse-proxy.git

# Accéder au répertoire
cd reverse-proxy
```

### 2. Installer les dépendances

```bash
# Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

**Dépendances installées :**
- `Flask` : Framework web pour l'interface
- `Gunicorn` : Serveur WSGI pour la production
- `requests` : Requêtes HTTP
- `email-validator` : Validation des emails
- `pyOpenSSL` : Gestion SSL/TLS

### 3. Configuration SSL initiale (une seule fois)

```bash
# Rendre les scripts exécutables
chmod +x setup_ssl.sh manage.py check_dns.py start-web.sh start-production.sh

# Installer Certbot et configurer le renouvellement automatique
sudo ./setup_ssl.sh
```

---

## 🎯 Utilisation

### 🌐 Option 1 : Interface Web (Recommandé)

#### Démarrage en mode développement

```bash
# Lancer l'interface web
./start-web.sh

# Ou manuellement
source venv/bin/activate
python3 web/app.py
```

**Accès :** `http://localhost:5000`

**Identifiants par défaut :**
- Username : `admin`
- Password : `admin`

⚠️ **Changez ces identifiants en production !**

#### Utilisation de l'interface

1. **Se connecter** à `http://localhost:5000`
2. **Dashboard** : Vue d'ensemble des sites et statistiques
3. **Créer un site** :
   - Cliquer sur "Sites" → "Nouveau site"
   - Remplir : domaine, port, SSL (optionnel)
   - Cliquer sur "Créer le site"
4. **Monitoring** : Voir le statut en temps réel
5. **SSL Check** : Vérifier les certificats et dates d'expiration

#### Démarrage en production

```bash
# Configurer la sécurité
cp .env.example .env.production
nano .env.production  # Modifier SECRET_KEY et ADMIN_PASSWORD

# Lancer en mode production (avec Gunicorn)
./start-production.sh
```

📚 **Guide complet :** Voir [web/README.md](web/README.md) et [PRODUCTION.md](PRODUCTION.md)

---

### 💻 Option 2 : Ligne de commande (CLI)

#### Vérifier la configuration DNS (recommandé)

```bash
python3 check_dns.py <domaine>
```

#### Créer un nouveau site

```bash
sudo python3 manage.py create <domaine> <port>
```

**Exemple :**
```bash
# Vérifier le DNS
python3 check_dns.py monsite.com

# Créer le site avec SSL
sudo python3 manage.py create monsite.com 8080
```

Le script vous demandera :
1. Votre email (pour Let's Encrypt, première fois seulement)
2. Si vous voulez installer le certificat SSL (recommandé : y)

**Résultat :**
- `http://monsite.com` → redirige vers `https://monsite.com`
- `https://monsite.com` → proxy vers `localhost:8080`
- Certificat SSL automatique et valide

#### Lister tous les sites

```bash
python3 manage.py list
```

#### Voir le statut détaillé

```bash
python3 manage.py status
```

Affiche pour chaque site :
- ✅ Statut Apache (activé/désactivé)
- 🔌 Statut du service sur le port
- 🔒 Statut SSL et jours restants avant expiration
- 📅 Date de création

#### Vérifier les certificats SSL

```bash
python3 manage.py check-ssl
```

Affiche :
- 📜 Liste de tous les certificats SSL
- 📅 Date d'expiration
- ⏰ Jours restants
- ⚠️ Alertes si expiration < 30 jours

#### Voir les statistiques

```bash
python3 manage.py stats
```

Affiche :
- 📊 Nombre total de sites
- ✅ Sites actifs vs inactifs
- 🔒 Répartition SSL/non-SSL
- 🔌 Distribution des ports

#### Supprimer un site

```bash
sudo python3 manage.py delete <domaine>
```

#### Renouveler les certificats SSL

```bash
sudo python3 manage.py renew-ssl
```

#### Créer un site sans SSL

```bash
sudo python3 manage.py create <domaine> <port> --no-ssl
```

#### Afficher la version

```bash
python3 manage.py version
```

---

## 🌟 Certificats Wildcard

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
📚 **Guide complet :** [WILDCARD_SSL_GUIDE.md](WILDCARD_SSL_GUIDE.md)

---

## 📖 Exemples Pratiques

### Exemple 1 : Site e-commerce avec interface web

1. **Lancer votre application** :
   ```bash
   # Application Node.js sur le port 3000
   npm start
   ```

2. **Ouvrir l'interface web** : `http://localhost:5000`

3. **Créer le site** :
   - Domaine : `boutique.com`
   - Port : `3000`
   - SSL : ✅ Activé

4. **Résultat** :
   - `http://boutique.com` → redirige vers `https://boutique.com`
   - `https://boutique.com` → proxy vers `localhost:3000`
   - Certificat SSL automatique et valide

### Exemple 2 : API Backend (CLI)

```bash
# API sur le port 8080
python3 check_dns.py api.monapp.com
sudo python3 manage.py create api.monapp.com 8080
```

### Exemple 3 : Application React

```bash
# App React en développement sur le port 3000
python3 check_dns.py app.exemple.com
sudo python3 manage.py create app.exemple.com 3000
```

### Exemple 4 : Plusieurs sous-domaines avec Wildcard

```bash
# Créer un certificat wildcard
sudo python3 manage.py install-wildcard-ssl '*.monapp.com'

# Créer plusieurs sites
sudo python3 manage.py create api.monapp.com 8080 --no-ssl
sudo python3 manage.py create app.monapp.com 3000 --no-ssl
sudo python3 manage.py create admin.monapp.com 5000 --no-ssl
```

---

## 📂 Architecture du Projet

```
reverse-proxy/
├── manage.py                    # Point d'entrée CLI principal
├── check_dns.py                 # Vérification DNS
├── setup_ssl.sh                 # Configuration SSL initiale
├── start-web.sh                 # Démarrage interface web (dev)
├── start-production.sh          # Démarrage production (Gunicorn)
├── requirements.txt             # Dépendances Python
├── .env.example                 # Template configuration
├── .env.production              # Configuration production
│
├── vhost_manager/               # Package principal (modulaire)
│   ├── __init__.py             # Exports du package
│   ├── core.py                 # Classe ApacheVHostManager
│   ├── config.py               # Gestion configuration JSON
│   ├── validation.py           # Validation domaines/ports
│   ├── ssl.py                  # Gestion certificats SSL
│   ├── monitoring.py           # Monitoring et statistiques
│   ├── utils.py                # Fonctions utilitaires
│   └── README.md               # Documentation du package
│
├── web/                         # Interface web Flask
│   ├── app.py                  # Application Flask
│   ├── requirements.txt        # Dépendances web
│   ├── README.md               # Documentation interface web
│   ├── static/                 # Fichiers statiques
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/              # Templates Jinja2
│       ├── base.html           # Template de base
│       ├── login.html          # Page de connexion
│       ├── dashboard.html      # Dashboard principal
│       ├── sites.html          # Liste des sites
│       ├── create_site.html    # Formulaire création
│       ├── monitoring.html     # Page monitoring
│       └── ssl_check.html      # Vérification SSL
│
├── tests/                       # Tests automatisés
│   ├── test_validation.py
│   ├── test_config.py
│   └── test_core.py
│
├── docs/                        # Documentation
│   ├── PRODUCTION.md           # Guide déploiement production
│   ├── WILDCARD_SSL_GUIDE.md   # Guide certificats wildcard
│   └── API.md                  # Documentation API (à venir)
│
└── vhost-manager-web.service   # Service systemd
```

---

## 📊 Structure des Fichiers Générés

```
/etc/apache2/sites-available/
├── monsite.com.conf              # Configuration Apache
└── api.monapp.com.conf           # Configuration Apache

/var/log/apache2/
├── monsite.com-access.log        # Logs d'accès HTTP
├── monsite.com-error.log         # Logs d'erreur HTTP
├── monsite.com-ssl-access.log    # Logs d'accès HTTPS
└── monsite.com-ssl-error.log     # Logs d'erreur HTTPS

/etc/letsencrypt/live/
├── monsite.com/                  # Certificats SSL
│   ├── fullchain.pem
│   ├── privkey.pem
│   └── cert.pem
└── api.monapp.com/               # Certificats SSL

/etc/vhost_manager.json           # Configuration du gestionnaire

/var/log/vhost-manager/           # Logs de l'interface web
├── manager.log                   # Logs généraux
├── access.log                    # Logs HTTP (Gunicorn)
└── error.log                     # Logs d'erreur (Gunicorn)
```

---

## 🔧 Configuration Avancée

### Modifier la configuration d'un site

Les fichiers de configuration se trouvent dans `/etc/apache2/sites-available/` :

```bash
sudo nano /etc/apache2/sites-available/monsite.com.conf
sudo systemctl reload apache2
```

### En-têtes de sécurité inclus

Chaque site HTTPS est configuré avec :
- `Strict-Transport-Security` (HSTS) : 1 an
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`

### Personnaliser l'interface web

```bash
# Modifier les identifiants
nano .env.production

# Générer une clé secrète
python3 -c 'import secrets; print(secrets.token_hex(32))'

# Modifier le port (défaut: 5000)
PORT=8080 python3 web/app.py
```

### Logs et surveillance

```bash
# Logs Apache en temps réel
sudo tail -f /var/log/apache2/monsite.com-access.log

# Logs de l'interface web
sudo tail -f /var/log/vhost-manager/access.log

# Logs d'erreurs SSL
sudo tail -f /var/log/apache2/monsite.com-ssl-error.log
```

---

## 🔄 Flux de Travail Complet

### Configuration d'un nouveau domaine

1. **Configurer le DNS** : Créer un enregistrement A pointant vers votre serveur
2. **Attendre la propagation DNS** (quelques minutes à quelques heures)
3. **Vérifier le DNS** :
   ```bash
   python3 check_dns.py nouveausite.com
   ```
4. **Créer le Virtual Host** :
   
   **Via l'interface web :**
   - Ouvrir `http://localhost:5000`
   - Sites → Nouveau site
   - Remplir le formulaire
   
   **Via CLI :**
   ```bash
   sudo python3 manage.py create nouveausite.com 8080
   ```

5. **Tester** : Naviguer vers `https://nouveausite.com`

### Vérification

```bash
# Vérifier que le site est actif
sudo a2query -s
apache2ctl -S

# Tester la configuration
sudo apache2ctl configtest

# Vérifier les certificats
sudo certbot certificates

# Via l'interface web
# → Monitoring → Voir le statut en temps réel
```

---

## 🛠️ Dépannage

### Erreur "DNS not found"

```bash
# Vérifier que votre enregistrement DNS A pointe vers votre serveur
dig monsite.com

# Attendre la propagation DNS (peut prendre jusqu'à 48h)
# Utiliser un vérificateur en ligne : https://dnschecker.org
```

### Erreur de certificat SSL

```bash
# Vérifier les logs Let's Encrypt
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Forcer le renouvellement
sudo certbot renew --force-renewal

# Vérifier la configuration Apache
sudo apache2ctl configtest
```

### Site inaccessible

```bash
# Vérifier si le service sur le port fonctionne
curl localhost:8080

# Vérifier les logs Apache
sudo tail -f /var/log/apache2/error.log

# Vérifier le statut via l'interface web
# → Monitoring → Voir les détails
```

### Port déjà utilisé

```bash
# Voir quels ports sont utilisés
sudo netstat -tulpn | grep :8080
sudo lsof -i :8080

# Tuer le processus si nécessaire
sudo kill -9 <PID>
```

### Interface web inaccessible

```bash
# Vérifier que Flask tourne
ps aux | grep python

# Vérifier les logs
sudo tail -f /var/log/vhost-manager/error.log

# Relancer l'interface
./start-web.sh
```

### Erreur "ModuleNotFoundError: No module named 'flask'" avec sudo

```bash
# Utiliser le script qui gère le venv
./start-web.sh

# Ou installer Flask globalement (non recommandé)
sudo pip3 install Flask
```

---

## 📚 Commandes Utiles

### Gestion Apache

```bash
# Lister tous les sites Apache actifs
sudo a2query -s

# Désactiver un site
sudo a2dissite monsite.com

# Activer un site
sudo a2ensite monsite.com

# Recharger Apache (sans interruption)
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

### Gestion de l'interface web

```bash
# Démarrer en mode développement
./start-web.sh

# Démarrer en mode production
./start-production.sh

# Installer comme service systemd
sudo cp vhost-manager-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vhost-manager-web
sudo systemctl start vhost-manager-web

# Voir le statut du service
sudo systemctl status vhost-manager-web

# Voir les logs du service
sudo journalctl -u vhost-manager-web -f
```

### Gestion SSL

```bash
# Lister tous les certificats
sudo certbot certificates

# Tester le renouvellement (test à blanc)
sudo certbot renew --dry-run

# Forcer le renouvellement
sudo certbot renew --force-renewal

# Révoquer un certificat
sudo certbot revoke --cert-path /etc/letsencrypt/live/monsite.com/cert.pem
```

---

## 🔐 Sécurité

### Bonnes pratiques incluses

- ✅ **HTTPS forcé** : Redirection automatique HTTP → HTTPS
- ✅ **HSTS activé** : Protection contre les attaques de rétrogradation
- ✅ **En-têtes de sécurité** : Protection XSS et clickjacking
- ✅ **Logs séparés** : Surveillance par domaine
- ✅ **Certificats valides** : Let's Encrypt reconnu par tous les navigateurs
- ✅ **Authentification web** : Accès protégé à l'interface
- ✅ **Mode production** : Logs silencieux, debug désactivé

### Configuration du pare-feu

```bash
# Avec UFW (Ubuntu)
sudo ufw allow 'Apache Full'
sudo ufw allow ssh
sudo ufw allow 5000/tcp  # Interface web (si accès externe)
sudo ufw enable

# Avec iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

### Sécuriser l'interface web en production

```bash
# 1. Changer les identifiants par défaut
nano .env.production
# SECRET_KEY=<clé_générée>
# ADMIN_USERNAME=votre_admin
# ADMIN_PASSWORD=MotDePasseFort123!

# 2. Créer un reverse proxy pour l'interface elle-même
sudo python3 manage.py create admin.votredomaine.com 5000

# 3. Limiter l'accès par IP (dans Apache)
# Ajouter dans /etc/apache2/sites-available/admin.votredomaine.com.conf :
<Location />
    Require ip 192.168.1.0/24
    Require ip 10.0.0.0/8
</Location>
```

📚 **Guide complet :** [PRODUCTION.md](PRODUCTION.md)

---

## 🔄 Renouvellement Automatique des Certificats

Le script de configuration SSL configure le renouvellement automatique via :
- **Timer systemd** (Ubuntu 20.04+)
- **Tâche cron** (solution de secours)

Les certificats sont renouvelés automatiquement tous les 90 jours.

Vérification manuelle :

```bash
# Tester le renouvellement (test à blanc)
sudo certbot renew --dry-run

# Forcer le renouvellement
sudo certbot renew --force-renewal

# Via l'interface web
# → SSL → Voir les dates d'expiration
```

---

## 📊 Surveillance et Maintenance

### Vérifier le statut des sites

**Via l'interface web :**
- Dashboard : Vue d'ensemble
- Monitoring : Statut en temps réel
- SSL : Vérification des certificats

**Via CLI :**
```bash
# Vérifier tous les sites gérés
python3 manage.py status

# Vérifier les Virtual Hosts Apache
sudo apache2ctl -S

# Vérifier l'expiration des certificats SSL
python3 manage.py check-ssl
```

### Surveillance des logs

```bash
# Surveiller tous les logs Apache
sudo tail -f /var/log/apache2/*.log

# Surveiller un domaine spécifique
sudo tail -f /var/log/apache2/monsite.com-*.log

# Surveiller l'interface web
sudo tail -f /var/log/vhost-manager/access.log

# Vérifier les erreurs SSL/TLS
sudo grep -i ssl /var/log/apache2/error.log
```

---

## 🚀 Déploiement en Production

### Installation sur un serveur

```bash
# 1. Cloner sur le serveur
cd /opt
sudo git clone https://github.com/Noubissie237/reverse-proxy.git
cd reverse-proxy

# 2. Installer les dépendances
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurer la sécurité
cp .env.example .env.production
nano .env.production  # Modifier SECRET_KEY et ADMIN_PASSWORD

# 4. Installer le service systemd
sudo cp vhost-manager-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vhost-manager-web
sudo systemctl start vhost-manager-web

# 5. Créer un reverse proxy pour l'interface
sudo python3 manage.py create admin.votredomaine.com 5000
```

📚 **Guide complet :** [PRODUCTION.md](PRODUCTION.md)

---

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install pytest pytest-cov

# Lancer les tests
pytest

# Avec couverture
pytest --cov=vhost_manager tests/

# Tests spécifiques
pytest tests/test_validation.py
```

---

## 📞 Support et Contribution

### Obtenir de l'aide

- 📖 **Documentation** : Voir les fichiers `.md` dans le projet
- 🐛 **Bugs** : [GitHub Issues](https://github.com/Noubissie237/reverse-proxy/issues)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/Noubissie237/reverse-proxy/discussions)

### Contribuer

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [Let's Encrypt](https://letsencrypt.org/) pour les certificats SSL gratuits
- [Apache HTTP Server](https://httpd.apache.org/) pour le serveur web
- [Flask](https://flask.palletsprojects.com/) pour le framework web
- [TailwindCSS](https://tailwindcss.com/) pour le design de l'interface
- La communauté open source

---

## 📚 Documentation Complète

- 📖 [Guide de Production](PRODUCTION.md) - Déploiement en production
- 🌐 [Interface Web](web/README.md) - Documentation de l'interface
- 🔒 [Certificats Wildcard](WILDCARD_SSL_GUIDE.md) - Guide des certificats wildcard
- 📦 [Package vhost_manager](vhost_manager/README.md) - Documentation du package

---

## 🎯 Roadmap

- [ ] API REST complète
- [ ] Authentification multi-utilisateurs
- [ ] Notifications par email
- [ ] Intégration Cloudflare
- [ ] Support Nginx
- [ ] Dashboard avec graphiques (Chart.js)
- [ ] Logs en direct dans l'interface
- [ ] Export/Import de configurations
- [ ] Mode sombre
- [ ] Application mobile

---

**💡 Pro Tip:** Ajoutez ces alias à votre `.bashrc` pour un accès rapide :

```bash
alias vhost='sudo python3 /opt/reverse-proxy/manage.py'
alias vhost-web='cd /opt/reverse-proxy && ./start-web.sh'
alias check-dns='python3 /opt/reverse-proxy/check_dns.py'
```

Puis utilisez simplement :
```bash
vhost create monsite.com 8080
vhost list
vhost status
check-dns monsite.com
```

---

<div align="center">

**⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile sur GitHub ! ⭐**

Made with ❤️ by [Noubissie237](https://github.com/Noubissie237)

</div>
