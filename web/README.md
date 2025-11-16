# 🌐 Apache VHost Manager - Interface Web

Interface web moderne pour gérer vos Virtual Hosts Apache via navigateur.

## ✨ Fonctionnalités

- 📊 **Dashboard** : Vue d'ensemble avec statistiques en temps réel
- 🌐 **Gestion des sites** : Créer, lister, supprimer des sites
- 📈 **Monitoring** : Statut en temps réel (Apache, ports, SSL)
- 🔒 **Vérification SSL** : Suivi des certificats et dates d'expiration
- 🔐 **Authentification** : Accès sécurisé par login/password
- 🎨 **Interface moderne** : Design responsive avec TailwindCSS

## 📦 Installation

### 1. Installer les dépendances

```bash
cd web
pip3 install -r requirements.txt
```

Ou depuis le dossier racine :

```bash
pip3 install Flask
```

### 2. Configuration (Optionnel)

Définir des variables d'environnement pour la sécurité :

```bash
export SECRET_KEY="votre-clé-secrète-aléatoire"
export ADMIN_USERNAME="votre-username"
export ADMIN_PASSWORD="votre-mot-de-passe-fort"
```

## 🚀 Lancement

### Méthode 1 : Script automatique (Recommandé) ⭐

```bash
# Le script gère automatiquement le venv et sudo
./start-web.sh
```

### Méthode 2 : Avec sudo et venv

```bash
# Activer le venv puis lancer avec sudo
source venv/bin/activate
sudo -E env PATH=$PATH python3 web/app.py
```

### Méthode 3 : Sans sudo (mode lecture seule)

```bash
python3 web/app.py
```

**Note :** Sans sudo, certaines fonctionnalités (création/suppression de sites) ne fonctionneront pas.

### ⚠️ Problème courant : Flask non trouvé avec sudo

Si vous obtenez `ModuleNotFoundError: No module named 'flask'` avec sudo :

```bash
# Solution 1 : Utiliser le script start-web.sh
./start-web.sh

# Solution 2 : Utiliser le Python du venv
sudo /chemin/vers/venv/bin/python3 web/app.py

# Solution 3 : Installer Flask globalement (non recommandé)
sudo pip3 install Flask
```

## 🌐 Accès

Une fois lancé, accédez à l'interface via :

```
http://localhost:5000
```

Ou depuis un autre appareil sur le réseau :

```
http://[IP-DU-SERVEUR]:5000
```

### Identifiants par défaut

- **Username :** `admin`
- **Password :** `admin`

⚠️ **IMPORTANT :** Changez ces identifiants en production !

## 📱 Pages disponibles

### Dashboard (`/`)
- Statistiques globales
- Alertes SSL
- Actions rapides
- Informations système

### Sites (`/sites`)
- Liste de tous les sites
- Statut en temps réel
- Actions (ouvrir, supprimer)

### Créer un site (`/sites/create`)
- Formulaire de création
- Configuration domaine + port
- Option SSL

### Monitoring (`/monitoring`)
- Statut détaillé par site
- Apache, Service, SSL
- Auto-refresh toutes les 30s

### SSL Check (`/ssl-check`)
- Liste des certificats
- Dates d'expiration
- Alertes automatiques

## 🔒 Sécurité

### En production

1. **Changez les identifiants par défaut**

```bash
export ADMIN_USERNAME="votre_username"
export ADMIN_PASSWORD="mot_de_passe_fort_123!"
```

2. **Utilisez une clé secrète forte**

```bash
export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
```

3. **Utilisez HTTPS**

Créez un reverse proxy pour l'interface web elle-même :

```bash
sudo python3 manage.py create admin.votredomaine.com 5000
```

4. **Limitez l'accès réseau**

Modifiez `app.py` pour écouter uniquement sur localhost :

```python
app.run(host='127.0.0.1', port=5000, debug=False)
```

Puis utilisez Apache comme reverse proxy.

## 🔧 Configuration avancée

### Changer le port

Dans `app.py`, ligne finale :

```python
app.run(host='0.0.0.0', port=8080, debug=True)  # Port 8080 au lieu de 5000
```

### Mode production

```python
app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False en production
```

### Utiliser avec Gunicorn (recommandé en production)

```bash
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🐛 Dépannage

### Erreur "Permission denied"

Lancez avec sudo :

```bash
sudo python3 web/app.py
```

### Port déjà utilisé

Changez le port dans `app.py` ou arrêtez le processus utilisant le port 5000 :

```bash
sudo lsof -i :5000
sudo kill -9 [PID]
```

### Erreur d'import `vhost_manager`

Assurez-vous d'être dans le bon répertoire :

```bash
cd /chemin/vers/reverse-proxy
python3 web/app.py
```

### Interface inaccessible depuis l'extérieur

Vérifiez le pare-feu :

```bash
sudo ufw allow 5000
```

## 📚 API Endpoints

L'interface expose également des endpoints API :

- `GET /api/sites` - Liste des sites (JSON)
- `GET /api/stats` - Statistiques (JSON)
- `POST /sites/<domain>/delete` - Supprimer un site

Exemple :

```bash
curl -H "Cookie: session=..." http://localhost:5000/api/stats
```

## 🎨 Personnalisation

### Thème

Les couleurs utilisent TailwindCSS. Pour personnaliser :

1. Modifiez les classes dans les templates
2. Couleur principale : `indigo` (changez vers `blue`, `purple`, etc.)

### Logo

Ajoutez votre logo dans `web/static/img/logo.png` et modifiez `base.html`.

## 📝 Structure des fichiers

```
web/
├── app.py                  # Application Flask principale
├── requirements.txt        # Dépendances Python
├── README.md              # Ce fichier
├── static/                # Fichiers statiques
│   ├── css/              # CSS personnalisés (vide, utilise TailwindCSS CDN)
│   ├── js/               # JavaScript personnalisés
│   └── img/              # Images
└── templates/            # Templates Jinja2
    ├── base.html         # Template de base
    ├── login.html        # Page de connexion
    ├── dashboard.html    # Dashboard principal
    ├── sites.html        # Liste des sites
    ├── create_site.html  # Formulaire création
    ├── monitoring.html   # Page monitoring
    └── ssl_check.html    # Vérification SSL
```

## 🚀 Évolutions futures

- [ ] WebSocket pour updates en temps réel
- [ ] Graphiques de monitoring (Chart.js)
- [ ] Gestion multi-utilisateurs
- [ ] Logs en direct dans l'interface
- [ ] Export des configurations
- [ ] API REST complète
- [ ] Mode sombre
- [ ] Notifications par email

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à ouvrir une issue ou une PR.

## 📄 Licence

Même licence que le projet principal.

---

**Version :** 1.0.0  
**Framework :** Flask 3.1.2  
**UI :** TailwindCSS + Font Awesome
