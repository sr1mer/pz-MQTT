#!/bin/bash

# MQTT Docker Compose Helper
# ============================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BROKER_DIR="$SCRIPT_DIR/broker"

echo "╔════════════════════════════════════════════╗"
echo "║  MQTT Docker Compose Manager - pz-MQTT    ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не встановлений!"
    echo ""
    echo "📥 Встановіть Docker з:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Docker Compose не знайдений (може бути інтегрований в Docker)"
fi

echo "✓ Docker знайдений: $(docker --version)"
echo ""

cd "$BROKER_DIR"

while true; do
    echo "Оберіть операцію:"
    echo "1. 🚀 Запустити MQTT брокер (docker compose up)"
    echo "2. 🛑 Зупинити MQTT брокер (docker compose down)"
    echo "3. 🔄 Перезапустити MQTT брокер"
    echo "4. 📊 Переглядати логи"
    echo "5. 🏥 Перевірити здоров'я контейнера"
    echo "6. 🗑️  Видалити вcе (очищення)"
    echo "7. 📱 Запустити Postman тести"
    echo "8. ❌ Вихід"
    echo ""
    read -p "Ваш вибір (1-8): " choice

    case $choice in
        1)
            echo ""
            echo "🚀 Запуск MQTT брокера..."
            docker compose up -d
            echo "✓ MQTT брокер запущений!"
            echo "  Адреса: mqtt://localhost:1883"
            echo "  WebSocket: ws://localhost:9090"
            docker compose ps
            ;;
        2)
            echo ""
            echo "🛑 Зупинення MQTT брокера..."
            docker compose down
            echo "✓ MQTT брокер зупинений!"
            ;;
        3)
            echo ""
            echo "🔄 Перезапуск MQTT брокера..."
            docker compose restart
            echo "✓ MQTT брокер перезапущений!"
            docker compose ps
            ;;
        4)
            echo ""
            echo "📊 Логи MQTT брокера (Ctrl+C для вихід):"
            echo "════════════════════════════════════════════"
            docker compose logs --follow mqtt-broker
            ;;
        5)
            echo ""
            echo "🏥 Перевірка здоров'я..."
            if docker compose ps | grep -q "healthy"; then
                echo "✓ Контейнер здоровий!"
            else
                docker compose ps
            fi
            ;;
        6)
            echo ""
            read -p "Ви впевнені? Всі дані будуть видалені (y/n): " confirm
            if [ "$confirm" = "y" ]; then
                docker compose down -v
                echo "✓ Все видалено!"
            fi
            ;;
        7)
            echo ""
            echo "📱 Постмен тести:"
            echo "1. Переконайтесь, що Postman встановлений"
            echo "2. Імпортуйте Postman_MQTT_Collection.json"
            echo "3. Використовуйте WebSocket: ws://localhost:9090"
            echo ""
            read -p "Натисніть Enter для продовження..."
            ;;
        8)
            echo "До побачення!"
            exit 0
            ;;
        *)
            echo "❌ Невірний вибір!"
            ;;
    esac

    echo ""
    read -p "Натисніть Enter для продовження..."
    clear
done
