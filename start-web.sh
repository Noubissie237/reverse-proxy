#!/bin/bash
#
# Script de démarrage de l'interface web Apache VHost Manager
# Lance l'application Flask avec les privilèges sudo et le venv activé
#

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Apache VHost Manager - Web Interface${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier si on est dans le bon répertoire
if [ ! -f "web/app.py" ]; then
    echo -e "${RED}❌ Erreur: Lancez ce script depuis le répertoire racine du projet${NC}"
    echo "   cd /chemin/vers/reverse-proxy"
    exit 1
fi

# Vérifier si le venv existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé${NC}"
    echo "   Création de l'environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
    echo ""
fi

# Activer le venv
source venv/bin/activate

# Vérifier si Flask est installé
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Flask n'est pas installé${NC}"
    echo "   Installation de Flask..."
    pip install Flask
    echo -e "${GREEN}✅ Flask installé${NC}"
    echo ""
fi

# Vérifier les privilèges sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Ce script nécessite les privilèges sudo${NC}"
    echo "   Relancement avec sudo..."
    echo ""
    
    # Relancer le script avec sudo en préservant le venv
    exec sudo -E env PATH="$PATH" VIRTUAL_ENV="$VIRTUAL_ENV" bash "$0" "$@"
fi

# Si on arrive ici, on a sudo et le venv est activé
echo -e "${GREEN}✅ Privilèges sudo: OK${NC}"
echo -e "${GREEN}✅ Environnement virtuel: OK${NC}"
echo ""

# Configuration
export FLASK_ENV=development
export FLASK_DEBUG=1

# Lancer l'application
echo -e "${GREEN}🌐 Lancement de l'interface web...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Utiliser le python du venv
exec python3 web/app.py
