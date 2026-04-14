#!/bin/bash
# ============================================================
#  Script de déploiement — Plateforme Hébergements Touristiques
#  Usage : copier-coller ce script sur le VPS
# ============================================================
set -e

echo "=========================================="
echo "  Déploiement Plateforme Hébergements"
echo "=========================================="

# --- 1. Mise à jour système + Docker ---
echo ">>> Installation des dépendances système..."
apt-get update -qq
apt-get install -y -qq docker.io docker-compose-plugin git curl ufw

# Démarrer Docker
systemctl enable docker
systemctl start docker

# --- 2. Firewall ---
echo ">>> Configuration du firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5050/tcp

# --- 3. Cloner le projet ---
echo ">>> Clonage du projet..."
PROJECT_DIR="/opt/plateforme_hebergements"
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    git pull origin main
else
    git clone https://github.com/ayoubrezala/plateforme_hebergements.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# --- 4. Clé API Anthropic ---
ENV_FILE="$PROJECT_DIR/.env"
if [ ! -f "$ENV_FILE" ] || ! grep -q "ANTHROPIC_API_KEY" "$ENV_FILE"; then
    echo ""
    echo "=========================================="
    echo "  Configuration de la clé API Claude"
    echo "=========================================="
    echo "Va sur https://console.anthropic.com/ → API Keys"
    echo "Génère une NOUVELLE clé et colle-la ici :"
    echo ""
    read -rp "ANTHROPIC_API_KEY=" API_KEY
    echo "ANTHROPIC_API_KEY=$API_KEY" > "$ENV_FILE"
    echo ">>> Clé enregistrée."
fi

# --- 5. Lancer les conteneurs ---
echo ">>> Build et lancement des conteneurs..."
docker compose down 2>/dev/null || true
docker compose up -d --build

# --- 6. Attendre que MariaDB soit prêt et lancer le pipeline ---
echo ">>> Exécution du pipeline ETL..."
docker compose run --rm pipeline

echo ""
echo "=========================================="
echo "  DÉPLOIEMENT TERMINÉ !"
echo "=========================================="
echo ""
echo "  🌐 Site web  : http://$(curl -s ifconfig.me):5050"
echo "  🤖 Chatbot   : intégré dans le site (bulle en bas à droite)"
echo "  📡 API       : http://$(curl -s ifconfig.me):5050/api/hebergements"
echo ""
echo "  Pour voir les logs : docker compose logs -f"
echo "=========================================="
