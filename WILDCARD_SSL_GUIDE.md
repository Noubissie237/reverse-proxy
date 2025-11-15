# 🌟 Guide des Certificats Wildcard SSL

## 📋 Qu'est-ce qu'un Certificat Wildcard ?

Un certificat wildcard (`*.example.com`) couvre **tous les sous-domaines** d'un domaine avec un seul certificat :

✅ **Couvert par `*.example.com` :**
- `api.example.com`
- `app.example.com`
- `admin.example.com`
- `blog.example.com`
- etc.

❌ **NON couvert :**
- `example.com` (domaine de base - nécessite un certificat séparé ou combiné)
- `sub.api.example.com` (sous-sous-domaine)

## 🔑 Différences avec les Certificats Standards

| Aspect | Standard | Wildcard |
|--------|----------|----------|
| **Domaines couverts** | 1 domaine spécifique | Tous les sous-domaines |
| **Validation** | HTTP-01 (fichier web) | DNS-01 (TXT record) |
| **Automatisation** | Totalement automatique | Manuel (ajout TXT DNS) |
| **Complexité** | Simple | Moyenne |
| **Cas d'usage** | Site unique | Multiple sous-domaines |

## 🚀 Utilisation

### Méthode 1 : Lors de la Création d'un Site

```bash
sudo python3 vhost_manager.py create '*.example.com' 8080
```

**Note :** Les guillemets sont **obligatoires** pour éviter que le shell n'interprète le `*`.

### Méthode 2 : Installation Séparée

```bash
sudo python3 vhost_manager.py install-wildcard-ssl '*.example.com'
```

## 📝 Processus Étape par Étape

### 1. Lancer la Commande

```bash
sudo python3 vhost_manager.py install-wildcard-ssl '*.example.com'
```

### 2. Confirmer l'Installation

Le script affichera :
```
🌟 Installing Wildcard SSL certificate for *.example.com
======================================================================

📋 Wildcard Certificate Information:
   Domain: *.example.com
   Base Domain: example.com
   Email: votre@email.com
   Challenge Type: DNS-01 (manual)

⚠️  IMPORTANT: Wildcard certificates require DNS validation
   You will need to add a TXT record to your DNS configuration.

Ready to proceed? (y/n):
```

Tapez `y` pour continuer.

### 3. Certbot Fournit le TXT Record

Certbot affichera quelque chose comme :
```
Please deploy a DNS TXT record under the name:
_acme-challenge.example.com

with the following value:
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Before continuing, verify the TXT record has been deployed.
```

### 4. Ajouter le TXT Record dans votre DNS

Connectez-vous à votre provider DNS (Cloudflare, OVH, AWS Route53, etc.) et ajoutez :

**Type :** TXT  
**Nom :** `_acme-challenge.example.com` ou `_acme-challenge`  
**Valeur :** `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`  
**TTL :** 300 (5 minutes) ou le minimum disponible

**Exemples par provider :**

#### Cloudflare
1. DNS → Add record
2. Type: TXT
3. Name: `_acme-challenge`
4. Content: [valeur fournie]
5. TTL: Auto

#### OVH
1. Zone DNS → Ajouter une entrée
2. Type: TXT
3. Sous-domaine: `_acme-challenge`
4. Valeur: [valeur fournie]
5. TTL: 300

#### AWS Route53
1. Hosted zones → Create record
2. Record type: TXT
3. Record name: `_acme-challenge.example.com`
4. Value: [valeur fournie]
5. TTL: 300

### 5. Vérifier la Propagation DNS

Avant de continuer dans certbot, vérifiez que le TXT record est visible :

```bash
# Méthode 1 : dig
dig _acme-challenge.example.com TXT

# Méthode 2 : nslookup
nslookup -type=TXT _acme-challenge.example.com

# Méthode 3 : host
host -t TXT _acme-challenge.example.com
```

Vous devriez voir la valeur du TXT record dans la réponse.

**⏱️ Temps de propagation :** 1-15 minutes (généralement 2-5 minutes)

### 6. Continuer dans Certbot

Une fois le TXT record vérifié, appuyez sur **Entrée** dans certbot.

### 7. Succès ! 🎉

Si tout s'est bien passé :
```
✅ Wildcard SSL certificate installed successfully!
📁 Certificate location: /etc/letsencrypt/live/example.com/
🔄 Automatic renewal is configured

💡 This certificate covers:
   - *.example.com (all subdomains)
   - example.com (base domain)
```

## 🔧 Utilisation du Certificat

### Pour un Nouveau Site

Le certificat wildcard sera automatiquement utilisé pour tous les sous-domaines :

```bash
sudo python3 vhost_manager.py create api.example.com 3000
sudo python3 vhost_manager.py create app.example.com 8080
sudo python3 vhost_manager.py create admin.example.com 5000
```

Tous utiliseront le même certificat wildcard !

### Configuration Apache Manuelle

Si vous configurez Apache manuellement, référencez le certificat :

```apache
SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem
SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem
```

## 🔄 Renouvellement

Les certificats wildcard se renouvellent comme les certificats standards :

```bash
sudo python3 vhost_manager.py renew-ssl
```

**⚠️ Important :** Le renouvellement nécessitera à nouveau l'ajout d'un TXT record DNS !

Pour un renouvellement automatique, vous devrez :
1. Utiliser un plugin DNS certbot (cloudflare, route53, etc.)
2. Ou configurer un hook de renouvellement manuel

## ❌ Dépannage

### Le TXT Record n'est pas Visible

**Causes possibles :**
- Propagation DNS pas encore terminée (attendre 5-15 minutes)
- Mauvais nom de record (doit être `_acme-challenge.example.com`)
- Erreur de saisie dans la valeur

**Solutions :**
```bash
# Vérifier avec plusieurs serveurs DNS
dig @8.8.8.8 _acme-challenge.example.com TXT
dig @1.1.1.1 _acme-challenge.example.com TXT
```

### Certbot Échoue à Valider

**Erreur :** `Incorrect TXT record`

**Solutions :**
1. Vérifier que le TXT record est exactement celui fourni par certbot
2. Supprimer les anciens TXT records `_acme-challenge`
3. Attendre plus longtemps pour la propagation DNS
4. Vérifier qu'il n'y a pas de guillemets autour de la valeur

### Le Certificat ne Couvre pas le Domaine de Base

Si vous voulez couvrir à la fois `*.example.com` ET `example.com`, utilisez :

```bash
# Lors de l'installation manuelle
certbot certonly --manual \
  --preferred-challenges dns \
  -d '*.example.com' \
  -d 'example.com'
```

Le script fait déjà cela automatiquement !

## 💡 Conseils et Bonnes Pratiques

### 1. Documenter le TXT Record
Gardez une trace de où et comment ajouter le TXT record pour les renouvellements futurs.

### 2. TTL Court
Utilisez un TTL court (300 secondes) pour les TXT records pour faciliter les changements.

### 3. Automatisation Future
Si vous gérez beaucoup de domaines, considérez :
- Utiliser un provider DNS avec API (Cloudflare, Route53)
- Installer les plugins certbot correspondants
- Automatiser complètement le processus

### 4. Tester Avant Production
Testez d'abord avec un sous-domaine de test avant de déployer en production.

### 5. Monitoring
Surveillez l'expiration avec :
```bash
python3 vhost_manager.py check-ssl
```

## 📚 Ressources

- [Let's Encrypt - Challenge Types](https://letsencrypt.org/docs/challenge-types/)
- [Certbot Documentation](https://eff-certbot.readthedocs.io/)
- [DNS Propagation Checker](https://dnschecker.org/)

## 🆘 Support

En cas de problème :
1. Vérifiez les logs : `/var/log/letsencrypt/letsencrypt.log`
2. Consultez `SSL_TROUBLESHOOTING.md`
3. Vérifiez la propagation DNS
4. Assurez-vous d'avoir les permissions DNS nécessaires

---

**Version :** 1.4.0  
**Dernière mise à jour :** 15 novembre 2024
