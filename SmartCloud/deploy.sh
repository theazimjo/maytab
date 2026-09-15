#!/bin/bash
# ==============================================================================
# SmartCloud DigitalOcean Deployment Script
# Manzil: http://104.248.43.194:1010
# ==============================================================================

set -e

echo "🚀 SmartCloud loyihasini o'rnatish va ishga tushirish boshlandi..."

# 1. Docker mavjudligini tekshirish
if ! command -v docker &> /dev/null; then
    echo "⚠️ Docker topilmadi! Docker va Compose o'rnatilmoqda..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# 2. Eskisini to'xtatish va Docker disk keshlari hamda ortiqcha xotirani tozalash
echo "📦 Eski konteynerlarni to'xtatish va disk xotirasini tozalash..."
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    DOCKER_COMPOSE_CMD="docker compose"
fi

$DOCKER_COMPOSE_CMD down || true

# Disk toza bo'lishi uchun ishlatilmayotgan Docker kesh va imedjlarni o'chirish
echo "🧹 Docker ishlatilmayotgan keshlarni tozalash (Disk joyini bo'shatish)..."
docker system prune -f || true
docker builder prune -f || true

# 3. Docker Imadjni qurish va Ishga tushirish
echo "🛠️ Docker image qurilmoqda..."
$DOCKER_COMPOSE_CMD build

echo "🟢 Konteyner fon rejimida ishga tushirilmoqda (Port: 1010)..."
$DOCKER_COMPOSE_CMD up -d

# 4. Migratsiya va Static fayllarni to'plash
echo "🔄 Baza migratsiyasi va static fayllar to'planmoqda..."
sleep 3
$DOCKER_COMPOSE_CMD exec -T smartcloud python manage.py migrate
$DOCKER_COMPOSE_CMD exec -T smartcloud python manage.py collectstatic --noinput

echo ""
echo "================================================================="
echo "✅ SmartCloud muvaffaqiyatli ishga tushirildi va o'rnatildi!"
echo "🌐 Server Manzili: http://104.248.43.194:1010"
echo "================================================================="
