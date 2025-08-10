#!/bin/bash

# Script de despliegue para EC2
set -e

echo "🚀 Iniciando despliegue..."

# Variables configurables
APP_DIR="/home/backend"
DOCKER_COMPOSE_FILE="$APP_DIR/docker-compose.yml"
BACKUP_DIR="/home/backend/backups"
CONTAINER_NAME="funds_backend"
COMPOSE_PROJECT_NAME="funds"

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

# Backup de la base de datos SQLite (si existe)
if [ -f "$APP_DIR/db.sqlite3" ]; then
    echo "📦 Creando backup de la base de datos..."
    cp "$APP_DIR/db.sqlite3" "$BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sqlite3"
fi

# Ir al directorio de la aplicación
cd $APP_DIR

# Pull de los últimos cambios
echo "📥 Actualizando código desde Git..."
git pull origin main

# Parar el contenedor actual de forma específica
echo "🛑 Deteniendo contenedor actual..."
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "🛑 Deteniendo contenedor $CONTAINER_NAME..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
else
    echo "ℹ️  Contenedor $CONTAINER_NAME no está corriendo"
fi

# Limpiar contenedores huérfanos del proyecto
echo "🧹 Limpiando contenedores huérfanos..."
docker compose -p $COMPOSE_PROJECT_NAME down --remove-orphans 2>/dev/null || true

# Reconstruir la imagen
echo "🔨 Reconstruyendo imagen Docker..."
docker compose build --no-cache

# Levantar los contenedores
echo "🚀 Levantando contenedores..."
docker compose up -d

# Verificar que el contenedor esté corriendo
echo "✅ Verificando estado del contenedor..."
sleep 10
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    echo "🎉 Despliegue completado exitosamente!"
    echo "📊 Estado del contenedor:"
    docker ps -f name=$CONTAINER_NAME
    echo "📋 Logs recientes:"
    docker logs --tail=10 $CONTAINER_NAME
else
    echo "❌ Error: El contenedor $CONTAINER_NAME no está corriendo"
    echo "📋 Últimos logs:"
    docker compose logs --tail=20
    exit 1
fi

# Limpiar imágenes Docker no utilizadas
echo "🧹 Limpiando imágenes Docker no utilizadas..."
docker image prune -f

echo "✨ Despliegue finalizado!"
