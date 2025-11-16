#!/bin/bash
#
# Script d'installation de l'Apache Agent
# Permet au conteneur Docker de gérer Apache sur l'hôte
#

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation de l'Apache Agent${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Vérifier les privilèges sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Ce script doit être exécuté avec sudo${NC}"
    exit 1
fi

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "apache-agent.py" ]; then
    echo -e "${RED}❌ Fichier apache-agent.py non trouvé${NC}"
    echo "   Exécutez ce script depuis le répertoire du projet"
    exit 1
fi

echo -e "${BLUE}Étape 1: Copie des fichiers${NC}"

# Copier le script de l'agent
INSTALL_DIR="/opt/apache-vhost-manager"
mkdir -p "$INSTALL_DIR"
cp apache-agent.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/apache-agent.py"
echo -e "${GREEN}✅ Script copié dans $INSTALL_DIR${NC}"

# Copier le service systemd
cp apache-agent.service /etc/systemd/system/
# Mettre à jour le chemin dans le service
sed -i "s|/root/reverse-proxy|$PWD|g" /etc/systemd/system/apache-agent.service
echo -e "${GREEN}✅ Service systemd installé${NC}"
echo ""

echo -e "${BLUE}Étape 2: Configuration du service${NC}"

# Recharger systemd
systemctl daemon-reload
echo -e "${GREEN}✅ Systemd rechargé${NC}"

# Activer le service
systemctl enable apache-agent.service
echo -e "${GREEN}✅ Service activé (démarrage automatique)${NC}"

# Démarrer le service
systemctl start apache-agent.service
echo -e "${GREEN}✅ Service démarré${NC}"
echo ""

echo -e "${BLUE}Étape 3: Vérification${NC}"

# Vérifier le statut
sleep 2
if systemctl is-active --quiet apache-agent.service; then
    echo -e "${GREEN}✅ Apache Agent fonctionne correctement${NC}"
    
    # Vérifier le socket
    if [ -S "/var/run/apache-agent.sock" ]; then
        echo -e "${GREEN}✅ Socket créé : /var/run/apache-agent.sock${NC}"
    else
        echo -e "${YELLOW}⚠️  Socket non trouvé, attendez quelques secondes...${NC}"
    fi
else
    echo -e "${RED}❌ Le service n'a pas démarré correctement${NC}"
    echo "   Vérifiez les logs : sudo journalctl -u apache-agent -n 50"
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation terminée !${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Commandes utiles :${NC}"
echo -e "  Voir les logs :      ${BLUE}sudo journalctl -u apache-agent -f${NC}"
echo -e "  Statut du service :  ${BLUE}sudo systemctl status apache-agent${NC}"
echo -e "  Redémarrer :         ${BLUE}sudo systemctl restart apache-agent${NC}"
echo -e "  Arrêter :            ${BLUE}sudo systemctl stop apache-agent${NC}"
echo ""
echo -e "${GREEN}Vous pouvez maintenant démarrer le conteneur Docker :${NC}"
echo -e "  ${BLUE}./docker-start.sh${NC}"
echo ""
