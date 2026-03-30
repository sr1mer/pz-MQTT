# pz-MQTT - MQTT Broker with Docker & Postman Testing

## 🚀 Quick Start

### 1. Start MQTT Broker

```bash
cd broker
docker compose up -d
```

**MQTT Broker runs on:**
- 🔵 **MQTT TCP**: `mqtt://localhost:1883`
- 🌐 **WebSocket**: `ws://localhost:9090`
- 🔐 **MQTT TLS**: `mqtts://localhost:8883`

### 2. Test with Postman

1. Open **Postman**
2. Click **Import** → Select `Postman_MQTT_Collection.json`
3. Use WebSocket connection on **port 9090**

OR create manually:
- New → Request
- URL: `ws://127.0.0.1:9090`
- Send test messages

### 3. Stop Broker

```bash
cd broker
docker compose down
```

## 📊 MQTT Topics for Testing

| Topic | Example Value | Description |
|-------|---|---|
| `test/topic` | `Hello MQTT!` | General test |
| `sensor/temperature` | `25.5` | Temperature |
| `sensor/humidity` | `65%` | Humidity |
| `device/status` | `online` | Device status |

## 🧪 Testing from Command Line

**Subscribe to topic:**
```bash
docker exec mqtt-broker-pz-mqtt mosquitto_sub -h localhost -t "test/topic"
```

**Publish message:**
```bash
docker exec mqtt-broker-pz-mqtt mosquitto_pub -h localhost -t "test/topic" -m "Hello MQTT!"
```

## 📝 Configuration Files

- **docker-compose.yml**: Docker environment setup
- **mosquitto.conf**: MQTT broker configuration
  - Port 1883: MQTT TCP
  - Port 8080: WebSocket (mapped to 9090 on host)

## ✅ Verification

Check if broker is running:
```bash
docker ps | findstr mqtt
```

Check connection:
```bash
docker exec mqtt-broker-pz-mqtt mosquitto_sub -h localhost -t '$SYS/broker/version' -C 1
```

## 🔗 Useful Links

- [Mosquitto Docs](https://mosquitto.org/)
- [MQTT Protocol](https://mqtt.org/)
- [Postman](https://www.postman.com/)
- [Docker](https://www.docker.com/)


---

## Getting started

### Варіант 1: Запуск через Docker (рекомендовано)

```bash
cd broker/
docker compose up
```

### Варіант 2: Запуск через Mosquitto локально (Windows)

```bash
# 1. MQTT брокер вже встановлений при запуску проекту
# 2. Дійте у папку mosquitto:
cd C:\Users\Артем\mosquitto

# 3. Запустіть брокер:
.\mosquitto.exe -v

# 4. У новому терміналі публікуйте повідомлення:
.\mosquitto_pub.exe -h 127.0.0.1 -p 1883 -t "test/topic" -m "Hello MQTT!"

# 5. Підпишіться на топік (у третьому терміналі):
.\mosquitto_sub.exe -h 127.0.0.1 -p 1883 -t "test/topic"
```

## Наявні топіки для тестування

Брокер готовий до роботи з наступними топіками:

- `test/topic` - загальний топік для тестування
- `sensor/temperature` - температурні дані
- `sensor/humidity` - дані вологості повітря
- `device/status` - статус пристроїв

## Основні MQTT команди

### Публікація повідомлення

```bash
mosquitto_pub -h 127.0.0.1 -p 1883 -t "topicName" -m "message"
```

Приклади:
```bash
mosquitto_pub -h 127.0.0.1 -p 1883 -t "test/topic" -m "Hello MQTT Broker!"
mosquitto_pub -h 127.0.0.1 -p 1883 -t "sensor/temperature" -m "25.5"
mosquitto_pub -h 127.0.0.1 -p 1883 -t "sensor/humidity" -m "65%"
```

### Підписка на топік

```bash
mosquitto_sub -h 127.0.0.1 -p 1883 -t "topicName"
```

Приклади:
```bash
mosquitto_sub -h 127.0.0.1 -p 1883 -t "test/topic"
mosquitto_sub -h 127.0.0.1 -p 1883 -t "sensor/+"  # підписка на всі sensor/*
mosquitto_sub -h 127.0.0.1 -p 1883 -t "#"          # підписка на ВСІ топіки
```

### Тестування через Node.js

```bash
# Встановіть залежність
npm install

# Запустіть тестовий клієнт
node mqtt-test-client.js
```

```
├── stt-pz-3
│   ├── broker/
│   │   ├── mqtt.conf              # конфігурація MQTT брокера
│   │   ├── docker-compose.yml     # Docker-конфігурація для розгортання
│   │   ├── mqtt_broker.py         # Простий MQTT брокер на Python
│   │   └── mosquitto.conf         # Конфігурація Mosquitto
│   ├── screenshots/               # докази роботи Publish/Subscribe
│   ├── mqtt-test-client.js        # Node.js тестовий MQTT клієнт
│   ├── .editorconfig              # налаштування редактора
│   ├── .gitignore                 # Git ігнор файли
│   ├── package.json               # NPM залежності
│   ├── README.md                  # Документація проекту
│   └── node_modules/              # встановлені пакети (не комітити)
└──

```

---

## MQTT Основні поняття

### Topic (Топік)
**Топік** - це адреса для публікації повідомлень. Це будується як ієрархія розділена прямими слешами `/`.

Приклади:
- `sensor/temperature` - температурні показники
- `building/floor1/room1/temperature` - 4-рівневий топік
- `home/+/temperature` - символ `+` замінює один рівень
- `home/#` - символ `#` замінює решту рівнів

### Publish (Публікація)
**Публікація** - це дія, коли клієнт надсилає повідомлення до певного топіка. Інші клієнти, які підписані на цей топік, отримають це повідомлення.

```bash
mosquitto_pub -h localhost -t "sensor/temp" -m "25.5"
```

### Subscribe (Підписка)
**Підписка** - це коли клієнт показує інтерес до певного топіка і хочет отримувати всі повідомлення опубліковані до цього топіка.

```bash
mosquitto_sub -h localhost -t "sensor/temp"
```

### QoS (Quality of Service)
**QoS** - це рівень гарантій доставки повідомлень:

- **QoS 0** - "At most once" (максимум один раз) - повідомлення може бути втрачено
- **QoS 1** - "At least once" (мінімум один раз) - повідомлення буде доставлено
- **QoS 2** - "Exactly once" (рівно один раз) - повідомлення буде доставлено рівно один раз

За замовчуванням застосовується QoS 0.

---

## Налаштування брокера

### Параметри Mosquitto:

| Параметр | Значення | Опис |
|----------|----------|------|
| `port` | 1883 | MQTT TCP порт |
| `allow_anonymous` | true | Дозволити анонімні підключення |
| `max_connections` | -1 | Не обмежувати кількість з'єднань |
| `persistence` | true | Зберігати дані на диск |
| `log_dest` | stdout | Логування на консоль |

---

## Результати тестування

✅ **Успішно протестовано:**

1. **Підключення до брокера**
   ```
   New client connected from 127.0.0.1 as auto-xxxx (p2, c1, k60)
   Sending CONNACK to auto-xxxx (0, 0)
   ```

2. **Публікація повідомлень**
   ```
   Received PUBLISH from auto-xxxx (d0, q0, r0, m0, 'test/topic', ... (18 bytes))
   ```

3. **Підписка на топіки**
   ```
   Received SUBSCRIBE from auto-xxxx
       test/topic (QoS 0)
   Sending SUBACK to auto-xxxx
   ```

4. **Обмін повідомленнями**
   - Топік: `test/topic` → Повідомлення: "Hello MQTT Broker!"
   - Топік: `sensor/temperature` → Значення: "25.5"
   - Топік: `sensor/humidity` → Значення: "65%"

---

## Useful links

[MQTT Essentials](https://www.hivemq.com/mqtt-essentials/)

[EMQX Documentation](https://www.emqx.io/docs/en/latest/)

[Eclipse Mosquitto](https://mosquitto.org/)

[MQTT with Postman](https://learning.postman.com/docs/sending-mqtt-messages/intro-to-mqtt/)

[NGINX API Gateway](https://docs.nginx.com/nginx/admin-guide/api-gateway/)

---

## 📁 Файлова структура проекту

```
pz-MQTT/
├── broker/
│   ├── mqtt.conf              # Конфігурація MQTT
│   ├── docker-compose.yml     # Docker-конфігурація
│   ├── mqtt_broker.py         # Python MQTT брокер
│   └── mosquitto.conf         # Mosquitto конфігурація
├── screenshots/
│   └── TESTING_REPORT.md      # Детальний звіт про тестування
├── node_modules/              # NPM пакети (не комітити)
├── .editorconfig              # Налаштування редактора
├── .gitignore                 # Git параметри ігнорування
├── package.json               # NPM залежності
├── mqtt-test-client.js        # MQTT тестовий клієнт на Node.js
├── mqtt-guide.sh              # Інтерактивний гайд (Linux/macOS)
├── docker-manager.sh          # Docker менеджер (Linux/macOS)
├── docker-manager.ps1         # Docker менеджер (Windows PowerShell)
├── Postman_MQTT_Collection.json # Postman колекція тестів
├── COMPLETION_REPORT.md       # Завершена звіт
├── DOCKER_POSTMAN_GUIDE.md    # Docker + Postman гайд
├── POSTMAN_MQTT_TESTING.md    # Postman MQTT тестування
└── README.md                  # Цей файл
```

---

## 📝 Примітки

### Встановлені інструменти:
- ✅ Eclipse Mosquitto 2.0.18 (MQTT брокер)
- ✅ Node.js 24.11.1 (для тестування)
- ✅ MQTT бібліотека для Node.js

### Адреси підключення:
- **MQTT (TCP):** `mqtt://127.0.0.1:1883`
- **WebSocket:** `ws://127.0.0.1:8080`
- **Брокер запущений:** ✅ Так

### Стан системи:
```
Компонент              Статус      Локація
─────────────────────────────────────────────────────
MQTT Брокер            ✅ Активний  127.0.0.1:1883
Node.js оточення       ✅ Готовий   v24.11.1
MQTT библиотека        ✅ Встановлена
Docker образи          ⚠️  Опціонально (потребує Docker)
Тестова документація   ✅ Готова   screenshots/
```

---

## 🐳 Docker + Postman Варіанти

### 🐳 Запуск через Docker

**Детально:** [DOCKER_POSTMAN_GUIDE.md](DOCKER_POSTMAN_GUIDE.md)

```bash
# 1. Встановіть Docker Desktop
# https://www.docker.com/products/docker-desktop

# 2. Запустіть контейнер
cd broker/
docker compose up -d

# 3. Перевірте статус
docker compose ps
docker compose logs -f mqtt-broker
```

### 📬 Тестування через Postman

**Детально:** [POSTMAN_MQTT_TESTING.md](POSTMAN_MQTT_TESTING.md)

**Варіант 1: WebSocket (Рекомендовано)**
- URL: `ws://127.0.0.1:8080`
- Публікація: `{"type":"publish","topic":"test/topic","payload":"Hello!"}`
- Підписка: `{"type":"subscribe","topics":["test/topic"]}`

**Варіант 2: Постман Колекція**
- Імпортуйте: `Postman_MQTT_Collection.json`
- Запустіть тести

**Варіант 3: Docker Manager (Інтерактивний)**

Windows (PowerShell):
```powershell
.\docker-manager.ps1
```

Linux/macOS:
```bash
chmod +x docker-manager.sh
./docker-manager.sh
```

---

## ✨ Успішно виконані завдання

- [x] Розгорнувте MQTT-брокер (Mosquitto)
- [x] Налаштувати базову конфігурацію сервісу
- [x] Ознайомитись із принципами роботи MQTT-протоколу
- [x] Виконати публікацію та підписку на MQTT-топіки
- [x] Перевірити працездатність сервісу через утиліти тестування
- [x] Документувати всі команди та налаштування
- [x] Надати докази роботи (логи, скріпти)

---

*Практичний урок pz-MQTT - 2026*