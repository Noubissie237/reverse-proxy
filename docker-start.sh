#!/bin/bash
#
# Script de démarrage Docker pour Apache VHost Manager
# Lance l'application en mode conteneurisé
#

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Apache VHost Manager - Docker Mode${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    echo "   Installez Docker : https://docs.docker.com/engine/install/"
    exit 1
fi

# Vérifier que Docker Compose est installé
if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
    echo "   Installez Docker Compose : https://docs.docker.com/compose/install/"
    exit 1
fi

# Vérifier que le fichier .env.production existe
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}⚠️  Fichier .env.production non trouvé${NC}"
    echo "   Création depuis .env.example..."
    cp .env.example .env.production
    echo -e "${GREEN}✅ Fichier .env.production créé${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Modifiez .env.production avec vos identifiants${NC}"
    echo "   1. Générez une clé secrète :"
    echo -e "      ${BLUE}python3 -c 'import secrets; print(secrets.token_hex(32))'${NC}"
    echo "   2. Modifiez .env.production avec :"
    echo "      - SECRET_KEY=<votre_clé_générée>"
    echo "      - ADMIN_USERNAME=<votre_username>"
    echo "      - ADMIN_PASSWORD=<mot_de_passe_fort>"
    echo ""
    read -p "Appuyez sur Entrée après avoir modifié .env.production..."
fi

# Vérifier la configuration de sécurité
source .env.production
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

echo -e "${GREEN}✅ Configuration vérifiée${NC}"
echo ""

# Créer le fichier de configuration des sites s'il n'existe pas
if [ ! -f "/etc/vhost_manager.json" ]; then
    echo -e "${YELLOW}⚠️  Fichier /etc/vhost_manager.json non trouvé${NC}"
    echo "   Création du fichier..."
    sudo touch /etc/vhost_manager.json
    sudo chmod 644 /etc/vhost_manager.json
    echo "{}" | sudo tee /etc/vhost_manager.json > /dev/null
    echo -e "${GREEN}✅ Fichier créé${NC}"
fi
echo ""

# Vérifier si le conteneur existe déjà
if docker ps -a --format '{{.Names}}' | grep -q "^vhost-manager-web$"; then
    echo -e "${YELLOW}⚠️  Le conteneur existe déjà${NC}"
    read -p "Voulez-vous le recréer ? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Arrêt et suppression du conteneur existant..."
        docker compose down
        echo -e "${GREEN}✅ Conteneur supprimé${NC}"
    fi
fi

# Construire et démarrer les conteneurs
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Construction de l'image Docker${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

docker compose build

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Démarrage des conteneurs${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

docker compose up -d

echo ""
echo -e "${GREEN}✅ Application démarrée avec succès !${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Informations d'accès${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "  URL:           ${GREEN}http://localhost:5000${NC}"
echo -e "  Username:      ${GREEN}${ADMIN_USERNAME}${NC}"
echo -e "  Logs:          ${BLUE}docker compose logs -f${NC}"
echo -e "  Status:        ${BLUE}docker compose ps${NC}"
echo -e "  Arrêter:       ${BLUE}docker compose stop${NC}"
echo -e "  Redémarrer:    ${BLUE}docker compose restart${NC}"
echo -e "  Supprimer:     ${BLUE}docker compose down${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Afficher les logs en temps réel (optionnel)
read -p "Voulez-vous voir les logs en temps réel ? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Logs en temps réel (Ctrl+C pour quitter)...${NC}"
    echo ""
    docker compose logs -f
fi
