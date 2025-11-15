# 📦 VHost Manager - Architecture Modulaire

## 🎯 Vue d'ensemble

Le code a été refactorisé en modules pour améliorer la maintenabilité et la lisibilité.

**Avant :** 1 fichier monolithique de 1201 lignes  
**Après :** 7 modules organisés de 1184 lignes au total

## 📁 Structure

```
vhost_manager/
├── __init__.py          (55 lignes)   - Point d'entrée du package
├── core.py              (308 lignes)  - Classe principale et gestion sites
├── ssl.py               (243 lignes)  - Gestion SSL (standard + wildcard)
├── monitoring.py        (287 lignes)  - Monitoring et statistiques
├── validation.py        (151 lignes)  - Validations (email, port, domaine)
├── config.py            (71 lignes)   - Gestion configuration JSON
└── utils.py             (69 lignes)   - Utilitaires (logging, commandes)

manage.py                (120 lignes)  - Script CLI principal
```

## 📋 Responsabilités des Modules

### `__init__.py`
- Exports du package
- Version du projet
- Imports centralisés

### `core.py`
**Classe principale :** `ApacheVHostManager`
- Création de sites (`create_site`)
- Suppression de sites (`delete_site`)
- Liste des sites (`list_sites`)
- Génération configuration Apache (`create_vhost_config`)
- Activation modules Apache (`enable_modules`)

### `ssl.py`
**Fonctions SSL :**
- `install_ssl_certificate()` - Certificats standards (HTTP-01)
- `install_wildcard_ssl_certificate()` - Certificats wildcard (DNS-01)
- `renew_ssl_certificates()` - Renouvellement
- `check_domain_dns()` - Vérification DNS

### `monitoring.py`
**Fonctions de monitoring :**
- `show_status()` - État détaillé des sites
- `check_ssl_certificates()` - Vérification certificats SSL
- `show_stats()` - Statistiques globales
- `check_site_status()` - Statut d'un site
- `get_ssl_certificate_info()` - Info certificat
- `check_port_in_use()` - Vérification port

### `validation.py`
**Fonctions de validation :**
- `validate_domain()` - Validation domaine
- `validate_port()` - Validation port
- `is_wildcard_domain()` - Détection wildcard
- `get_base_domain()` - Extraction domaine de base
- `validate_wildcard_domain()` - Validation wildcard
- `get_validated_email()` - Validation email

### `config.py`
**Classe :** `ConfigManager`
- `load_config()` - Chargement configuration
- `save_config()` - Sauvegarde configuration
- `add_site()` - Ajout site
- `remove_site()` - Suppression site
- `get_site()` - Récupération site
- `site_exists()` - Vérification existence

### `utils.py`
**Fonctions utilitaires :**
- `setup_logging()` - Configuration logging
- `run_command()` - Exécution commandes shell
- `check_sudo()` - Vérification privilèges

### `manage.py`
**Script CLI :**
- Point d'entrée principal
- Parsing arguments
- Dispatch vers les bonnes fonctions
- Gestion erreurs

## 🔄 Migration depuis l'ancien code

### Ancien usage
```python
from vhost_manager import ApacheVHostManager
manager = ApacheVHostManager()
manager.create_site("example.com", 8080)
```

### Nouveau usage (identique !)
```python
from vhost_manager import ApacheVHostManager
manager = ApacheVHostManager()
manager.create_site("example.com", 8080)
```

**Aucun changement nécessaire !** L'API publique reste identique.

## 🧪 Tests

Les tests ont été mis à jour pour utiliser les nouveaux modules :

```python
# Avant
from vhost_manager import ApacheVHostManager

# Après
from vhost_manager.core import ApacheVHostManager
from vhost_manager.validation import validate_domain
from vhost_manager.monitoring import check_site_status
```

**Résultat :** 27/27 tests passent ✅

## 📊 Avantages de la Modularisation

### ✅ Maintenabilité
- Code organisé par responsabilité
- Plus facile à comprendre
- Modifications isolées

### ✅ Testabilité
- Tests unitaires par module
- Mocking plus facile
- Tests plus rapides

### ✅ Réutilisabilité
- Fonctions importables individuellement
- Pas besoin de tout importer
- Meilleure séparation des concerns

### ✅ Collaboration
- Plusieurs développeurs peuvent travailler en parallèle
- Moins de conflits Git
- Code review plus facile

### ✅ Performance
- Import sélectif (moins de mémoire)
- Chargement plus rapide
- Meilleure organisation du cache Python

## 🚀 Utilisation

### CLI (inchangé)
```bash
python3 manage.py create example.com 8080
python3 manage.py status
python3 manage.py check-ssl
```

### Import programmatique
```python
# Import complet
from vhost_manager import ApacheVHostManager

# Import sélectif
from vhost_manager.validation import validate_domain, validate_port
from vhost_manager.ssl import install_ssl_certificate
from vhost_manager.monitoring import show_status
```

## 📝 Conventions de Code

### Imports
- Imports standards en premier
- Imports tiers ensuite
- Imports locaux en dernier

### Docstrings
- Format Google style
- Args, Returns, Raises documentés
- Exemples si nécessaire

### Logging
- Utiliser `logger` de `utils.py`
- Niveaux appropriés (INFO, WARNING, ERROR)
- Messages descriptifs

## 🔮 Évolutions Futures

La structure modulaire facilite l'ajout de nouvelles fonctionnalités :

- **`vhost_manager/backup.py`** - Sauvegarde/restauration
- **`vhost_manager/api.py`** - API REST
- **`vhost_manager/dns_providers/`** - Intégrations DNS
- **`vhost_manager/templates/`** - Templates de configuration

## 📚 Ressources

- **Documentation principale :** `../README.md`
- **Guide wildcard SSL :** `../WILDCARD_SSL_GUIDE.md`
- **Tests :** `../tests/`
- **Dépannage SSL :** `../SSL_TROUBLESHOOTING.md`

---

**Version :** 1.5.0  
**Architecture :** Modulaire  
**Lignes de code :** 1184 (vs 1201 monolithique)  
**Modules :** 7  
**Tests :** 27 ✅
