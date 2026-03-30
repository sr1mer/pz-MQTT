# 🐳 MQTT + Docker + Postman - Детальний Гайд

## 📋 Зміст

1. [Встановлення Docker](#встановлення-docker)
2. [Запуск MQTT через Docker](#запуск-mqtt-через-docker)
3. [Налаштування Postman](#налаштування-postman)
4. [Тестування через Postman](#тестування-через-postman)
5. [Альтернативні варіанти](#альтернативні-варіанти)

---

## 🐳 Встановлення Docker

### Для Windows 10/11

#### Варіант 1: Docker Desktop (Рекомендуємо)

1. **Завантажте Docker Desktop:**
   ```
   https://www.docker.com/products/docker-desktop
   ```

2. **Встановіть Docker:**
   - Запустіть installer
   - Виберіть опцію "Install required Windows components"
   - Після встановлення перезавантажте комп'ютер

3. **Перевірте встановлення:**
   ```powershell
   docker --version
   docker run hello-world
   ```

#### Варіант 2: Docker через WSL 2 (Advanced)

```powershell
# 1. Встановіть WSL 2
wsl --install

# 2. Встановіть Docker Desktop з підтримкою WSL 2

# 3. Перевірте
docker ps
```

### Для Linux (Ubuntu/Debian)

```bash
# Встановіть Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Дозвольте користувачу користуватися Docker
sudo usermod -aG docker $USER
newgrp docker

# Перевірте
docker --version
```

### Для macOS

```bash
# Через Homebrew (рекомендовано)
brew install --cask docker

# Або завантажте Docker Desktop з
# https://www.docker.com/products/docker-desktop
```

---

## 🚀 Запуск MQTT через Docker

### 1. Перевірте структуру файлів

```
pz-MQTT/
├── broker/
│   ├── docker-compose.yml    ← Конфігурація Docker
│   ├── mosquitto.conf         ← Конфігурація MQTT
│   └── ...
└── ...
```

### 2. Запустіть Docker Compose

```powershell
# Перейдіть у папку з docker-compose.yml
cd C:\Users\Артем\pz-MQTT\broker

# Запустіть контейнер
docker compose up -d

# Перевірте статус
docker compose ps

# Переглядайте логи
docker compose logs -f mqtt-broker
```

### 3. Результати запуску

```
✓ Контейнер mqtt-broker-pz-mqtt запущений
✓ Порт 1883 (MQTT) доступний
✓ Порт 8080 (WebSocket) доступний
✓ Дані зберігаються у Volumes
```

### 4. Команди керування

```powershell
# Зупинити контейнер
docker compose down

# Перезапустити
docker compose restart

# Видалити містить та обсяги
docker compose down -v

# Переглядати логи в реальному часі
docker compose logs --follow mqtt-broker

# Виконати команду всередині контейнера
docker compose exec mqtt-broker mosquitto_pub -h localhost -t test/topic -m "Hello"
```

---

## 📬 Налаштування Postman

### 1. Встановіть Postman

**Завантажте з:** https://www.postman.com/downloads/

### 2. Імпортуйте MQTT колекцію

1. Відкрийте Postman
2. Натисніть **Import** → **File**
3. Виберіть файл: `Postman_MQTT_Collection.json`
4. Колекція буде додана до вашого Workspace

### 3. Налаштуйте Environment (Постійна)

1. Перейдіть на вкладку **Environment** (праворуч)
2. Натисніть **New**
3. Назвіть: `MQTT Local`
4. Додайте змінні:

```json
{
  "mqtt_host": "127.0.0.1",
  "mqtt_port": "1883",
  "mqtt_ws_port": "8080",
  "mqtt_broker_url": "mqtt://127.0.0.1:1883"
}
```

---

## 🧪 Тестування через Postman

### Варіант 1: MQTT Protocol (Native)

Postman мав підтримку MQTT дослідже планів на його розширення.

### Варіант 2: WebSocket (Через Postman)

1. **Відкрийте нову вкладку**
2. **Виберіть WebSocket**
3. **URL:**
   ```
   ws://127.0.0.1:8080
   ```
4. **Натисніть Connect**
5. **Надсилайте MQTT повідомлення як JSON:**

   ```json
   {
     "topic": "test/topic",
     "payload": "Hello from Postman!",
     "qos": 0
   }
   ```

### Варіант 3: REST API Bridge (Рекомендовано)

Якщо ваш MQTT брокер підтримує REST API:

**Публікація:**
```
POST http://127.0.0.1:8080/api/v1/mqtt/publish
Content-Type: application/json

{
  "topic": "test/topic",
  "payload": "Hello MQTT!",
  "qos": 0,
  "retain": false
}
```

**Підписка:**
```
GET http://127.0.0.1:8080/api/v1/mqtt/subscribe?topic=test/topic
```

---

## 🔧 Advanced: Налаштування mosquitto.conf для Postman

Відредагуйте `broker/mosquitto.conf`:

```bash
listener 1883
protocol mqtt
allow_anonymous true

listener 8080
protocol websockets
allow_anonymous true

# Для REST API (опціонально)
# plugin /mosquitto/go-auth.so
# plugin_opt_backends files
# auth_plugin /mosquitto/go-auth.so
```

---

## 📊 Приклади команд Curl (для тестування)

Замість Postman можна використовувати Curl:

### Публікація через MQTT CLI

```powershell
# Потребує mosquitto-клієнта
mosquitto_pub -h 127.0.0.1 -p 1883 -t "test/topic" -m "Hello Docker MQTT!"

# Крізь Docker контейнер
docker compose exec mqtt-broker mosquitto_pub -h localhost -t test/topic -m "Docker Test"
```

### Підписка через MQTT CLI

```powershell
# Локальна підписка
mosquitto_sub -h 127.0.0.1 -p 1883 -t "test/topic"

# Крізь Docker контейнер
docker compose exec mqtt-broker mosquitto_sub -h localhost -t test/topic
```

---

## 🐛 Усунення Проблем

### Проблема: Docker не знаходиться
```powershell
# Перевірте установку
docker --version

# Додайте Docker до PATH (якщо потрібно)
$env:Path += ";C:\Program Files\Docker\Docker\resources\bin"
```

### Проблема: Порт 1883 вже використовується
```powershell
# Знайдіть процес
netstat -ano | findstr 1883

# Вибийте процес (замініть PID)
taskkill /PID 1234 /F

# Або змініть порт у docker-compose.yml
# ports:
#   - "1884:1883"
```

### Проблема: WebSocket не працює
```
# Переконайтесь в docker-compose.yml
listener 8080
protocol websockets

# Перезапустите контейнер
docker compose restart
```

---

## ✅ Чек-Лист Завершення

- [ ] Docker встановлений і працює
- [ ] MQTT контейнер запущений (`docker compose up`)
- [ ] Порти 1883 та 8080 доступні
- [ ] Postman встановлений
- [ ] Колекція `Postman_MQTT_Collection.json` імпортована
- [ ] Environment `MQTT Local` налаштований
- [ ] Успішна публікація через Postman/WebSocket
- [ ] Успішна підписка та отримання повідомлень
- [ ] Логи показують активність (видимо через Docker)

---

## 📚 Корисні Посилання

- [Docker Documentation](https://docs.docker.com/)
- [Mosquitto Docker Image](https://hub.docker.com/_/eclipse-mosquitto)
- [Postman Learning Center](https://learning.postman.com/)
- [MQTT WebSocket Protocol](https://mqtt.org/software/use_cases/libraries)
- [Postman WebSocket Support](https://learning.postman.com/docs/sending-requests/requests/)

---

## 🎯 Наступні кроки

1. ✅ Встановіть Docker
2. ✅ Запустіть MQTT через Docker
3. ✅ Налаштуйте Postman
4. ✅ Виконайте тестування
5. ✅ Документуйте результати

**Готово до завдання pz-MQTT з Docker та Postman!**
