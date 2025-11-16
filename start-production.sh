#!/bin/bash
#
# Script de démarrage PRODUCTION de l'interface web
# Lance l'application avec Gunicorn (serveur WSGI production)
#

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Apache VHost Manager - Production Mode${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Vérifier le répertoire
if [ ! -f "web/app.py" ]; then
    echo -e "${RED}❌ Erreur: Lancez ce script depuis le répertoire racine du projet${NC}"
    exit 1
fi

# Charger la configuration production
if [ -f ".env.production" ]; then
    echo -e "${GREEN}✅ Chargement de .env.production${NC}"
    export $(cat .env.production | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  Fichier .env.production non trouvé${NC}"
    echo -e "   Utilisation des valeurs par défaut"
    export FLASK_ENV=production
    export VHOST_VERBOSE=0
fi

# Vérifier le venv
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé${NC}"
    echo "   Création..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
else
    source venv/bin/activate
    echo -e "${GREEN}✅ Environnement virtuel activé${NC}"
fi

# Vérifier Gunicorn
if ! python3 -c "import gunicorn" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Gunicorn n'est pas installé${NC}"
    echo "   Installation..."
    pip install -q gunicorn
    echo -e "${GREEN}✅ Gunicorn installé${NC}"
fi

# Vérifier sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Ce script nécessite les privilèges sudo${NC}"
    echo "   Relancement avec sudo..."
    echo ""
    exec sudo -E env PATH="$PATH" VIRTUAL_ENV="$VIRTUAL_ENV" bash "$0" "$@"
fi

echo -e "${GREEN}✅ Privilèges sudo: OK${NC}"
echo ""

# Vérifier la configuration de sécurité
if [ "$SECRET_KEY" == "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY" ] || [ "$ADMIN_PASSWORD" == "CHANGE_THIS_PASSWORD" ]; then
    echo -e "${RED}═══════════════════════════════════════════════${NC}"
    echo -e "${RED}  ⚠️  AVERTISSEMENT DE SÉCURITÉ ⚠️${NC}"
    echo -e "${RED}═══════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Vous utilisez les identifiants par défaut !${NC}"
    echo ""
    echo "Générez une clé secrète sécurisée :"
    echo -e "${BLUE}python3 -c 'import secrets; print(secrets.token_hex(32))'${NC}"
    echo ""
    echo "Puis modifiez .env.production avec :"
    echo "  - SECRET_KEY=<votre_clé_générée>"
    echo "  - ADMIN_PASSWORD=<mot_de_passe_fort>"
    echo ""
    read -p "Continuer quand même ? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Configuration Gunicorn
WORKERS=${WORKERS:-4}
BIND=${HOST:-0.0.0.0}:${PORT:-5000}
TIMEOUT=${TIMEOUT:-120}
ACCESS_LOG=${ACCESS_LOG:-/var/log/vhost-manager/access.log}
ERROR_LOG=${ERROR_LOG:-/var/log/vhost-manager/error.log}

# Créer le répertoire de logs
mkdir -p /var/log/vhost-manager

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Configuration${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "  Mode:          ${GREEN}PRODUCTION${NC}"
echo -e "  Workers:       ${WORKERS}"
echo -e "  Bind:          ${BIND}"
echo -e "  Timeout:       ${TIMEOUT}s"
echo -e "  Access Log:    ${ACCESS_LOG}"
echo -e "  Error Log:     ${ERROR_LOG}"
echo -e "  Verbose:       ${VHOST_VERBOSE}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Lancer Gunicorn
echo -e "${GREEN}🚀 Démarrage de Gunicorn...${NC}"
echo ""

cd web
exec gunicorn \
    --workers $WORKERS \
    --bind $BIND \
    --timeout $TIMEOUT \
    --access-logfile $ACCESS_LOG \
    --error-logfile $ERROR_LOG \
    --log-level info \
    --capture-output \
    app:app
