# Apache Virtual Host Manager - Production Dockerfile
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Noubissie237"
LABEL description="Apache Virtual Host Manager Web Interface"
LABEL version="1.5.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root avec sudo
RUN useradd -m -s /bin/bash vhostmanager && \
    echo "vhostmanager ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY --chown=vhostmanager:vhostmanager . .

# Créer les répertoires nécessaires
RUN mkdir -p /var/log/vhost-manager && \
    chown -R vhostmanager:vhostmanager /var/log/vhost-manager

# Exposer le port de l'application
EXPOSE 5000

# Passer à l'utilisateur non-root
USER vhostmanager

# Healthcheck pour vérifier que l'application fonctionne
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/login || exit 1

# Commande de démarrage avec Gunicorn
CMD ["gunicorn", \
    "--chdir", "web", \
    "--workers", "4", \
    "--bind", "0.0.0.0:5000", \
    "--timeout", "120", \
    "--access-logfile", "/var/log/vhost-manager/access.log", \
    "--error-logfile", "/var/log/vhost-manager/error.log", \
    "--log-level", "info", \
    "--capture-output", \
    "app:app"]
