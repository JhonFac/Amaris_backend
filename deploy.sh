#!/bin/bash

# Script de despliegue para EC2
set -e

echo "🚀 Iniciando despliegue..."

# Variables configurables
APP_DIR="/home/backend/Amaris_backend"
DOCKER_COMPOSE_FILE="$APP_DIR/docker-compose.yml"
CONTAINER_NAME="funds_backend"
COMPOSE_PROJECT_NAME="funds"

# Pull de los últimos cambios
echo "📥 Actualizando código desde Git..."
# git pull origin main
git fetch origin main
git reset --hard origin/main

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
docker-compose -f $DOCKER_COMPOSE_FILE build

# Levantar los contenedores
echo "🚀 Levantando contenedores..."
docker-compose -f $DOCKER_COMPOSE_FILE up -d

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
