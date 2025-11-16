# Architecture Docker avec Apache Agent

## Problème résolu

Le conteneur Docker ne peut pas exécuter directement les commandes Apache (`a2ensite`, `a2dissite`, `systemctl`) sur l'hôte car Apache tourne en dehors du conteneur.

## Solution : Apache Agent

Un service léger qui tourne sur l'hôte et écoute les commandes du conteneur via un socket Unix.

### Architecture

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
│                        /var/run/apache-    │
│                         agent.sock         │
│                                 │          │
│  ┌──────────────────────────────┼────────┐ │
│  │    Conteneur Docker          │        │ │
│  │                               │        │ │
│  │  ┌────────────────────────────▼─────┐ │ │
│  │  │  VHost Manager Web (Flask)      │ │ │
│  │  │  - Interface web (port 5000)    │ │ │
│  │  │  - Communique via socket        │ │ │
│  │  └─────────────────────────────────┘ │ │
│  └──────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## Installation

### Étape 1 : Installer l'Apache Agent sur l'hôte

```bash
cd ~/reverse-proxy
chmod +x install-apache-agent.sh
sudo ./install-apache-agent.sh
```

Le script va :
- ✅ Copier `apache-agent.py` dans `/opt/apache-vhost-manager/`
- ✅ Installer le service systemd
- ✅ Démarrer l'agent automatiquement
- ✅ Créer le socket `/var/run/apache-agent.sock`

### Étape 2 : Démarrer le conteneur Docker

```bash
./docker-start.sh
```

Le conteneur va automatiquement détecter le socket et utiliser l'agent.

## Vérification

### Vérifier que l'agent fonctionne

```bash
# Statut du service
sudo systemctl status apache-agent

# Logs en temps réel
sudo journalctl -u apache-agent -f

# Vérifier le socket
ls -la /var/run/apache-agent.sock
```

### Tester depuis le conteneur

```bash
# Accéder au conteneur
docker compose exec vhost-manager bash

# Vérifier que le socket est accessible
ls -la /var/run/apache-agent.sock

# Tester une commande
python3 -c "
from vhost_manager.apache_client import apache_client
result = apache_client.check_status()
print(result)
"
```

## Commandes Apache supportées

L'agent supporte les commandes suivantes :

- `a2ensite <domain>` - Activer un site
- `a2dissite <domain>` - Désactiver un site
- `a2enmod <module>` - Activer un module
- `systemctl reload apache2` - Recharger Apache
- `systemctl restart apache2` - Redémarrer Apache
- `apache2ctl configtest` - Tester la configuration
- `systemctl is-active apache2` - Vérifier le statut

## Dépannage

### L'agent ne démarre pas

```bash
# Voir les logs détaillés
sudo journalctl -u apache-agent -n 100

# Vérifier les permissions
sudo ls -la /var/run/apache-agent.sock

# Redémarrer l'agent
sudo systemctl restart apache-agent
```

### Le conteneur ne trouve pas le socket

```bash
# Vérifier que le socket existe
ls -la /var/run/apache-agent.sock

# Vérifier le montage dans le conteneur
docker compose exec vhost-manager ls -la /var/run/apache-agent.sock

# Redémarrer le conteneur
docker compose restart
```

### Les commandes échouent

```bash
# Voir les logs de l'agent
sudo journalctl -u apache-agent -f

# Tester manuellement
echo '{"action":"apache_status","params":{}}' | nc -U /var/run/apache-agent.sock
```

## Sécurité

- ✅ Le socket est accessible uniquement localement
- ✅ Seules les commandes Apache sont autorisées
- ✅ L'agent tourne avec les privilèges root (nécessaire pour Apache)
- ✅ Le conteneur communique via un socket Unix (pas de réseau)

## Désinstallation

```bash
# Arrêter et désactiver le service
sudo systemctl stop apache-agent
sudo systemctl disable apache-agent

# Supprimer les fichiers
sudo rm /etc/systemd/system/apache-agent.service
sudo rm -rf /opt/apache-vhost-manager
sudo rm /var/run/apache-agent.sock

# Recharger systemd
sudo systemctl daemon-reload
```

## Avantages

1. **Sécurité** : Le conteneur ne peut exécuter que des commandes Apache spécifiques
2. **Isolation** : Apache reste sur l'hôte, le conteneur gère uniquement l'interface
3. **Simplicité** : Pas besoin de monter `/var/run/systemd` ou d'autres ressources système
4. **Performance** : Communication rapide via socket Unix
5. **Fiabilité** : L'agent redémarre automatiquement en cas de problème

## Logs

- **Agent** : `/var/log/vhost-manager/apache-agent.log`
- **Application** : `/var/log/vhost-manager/error.log`
- **Systemd** : `journalctl -u apache-agent`
