#!/usr/bin/env python3
"""
MQTT to SMS Web Dashboard
Слухає MQTT повідомлення та показує їх в веб-інтерфейсі
"""

import paho.mqtt.client as mqtt
import json
import os
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import sqlite3
from pathlib import Path

# Конфігурація
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
SMS_TOPIC = "sms/send"  # Топік для СМС
DB_FILE = "sms_messages.db"
WEB_PORT = 8000

# Глобальна база А для зберігання повідомлень
messages = []
max_messages = 100


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP сервер з підтримкою потоків"""
    daemon_threads = True


class SMSRequestHandler(SimpleHTTPRequestHandler):
    """Обробник HTTP запитів"""
    
    def do_GET(self):
        """GET запити"""
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(get_html_content().encode("utf-8"))
        elif self.path == "/api/messages":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(messages, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/api/clear":
            global messages
            messages = []
            save_to_db([])
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "cleared"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """POST запити"""
        if self.path == "/api/send-sms":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                data = json.loads(body)
                phone = data.get("phone", "Unknown")
                message = data.get("message", "")
                
                # Добавити повідомлення
                msg_obj = {
                    "id": len(messages) + 1,
                    "phone": phone,
                    "text": message,
                    "timestamp": datetime.now().isoformat(),
                    "type": "sent"
                }
                messages.insert(0, msg_obj)
                if len(messages) > max_messages:
                    messages.pop()
                
                save_to_db(messages)
                
                # Опублікувати в MQTT
                mqtt_client.publish(SMS_TOPIC, json.dumps({
                    "phone": phone,
                    "message": message
                }), qos=1)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "sent", "id": msg_obj["id"]}).encode())
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Приховати логи запитів"""
        if "/api/" not in args[0]:
            super().log_message(format, *args)


def init_database():
    """Ініціалізувати базу даних"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sms_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            type TEXT DEFAULT 'sent'
        )
    """)
    conn.commit()
    conn.close()


def load_from_db():
    """Завантажити повідомлення з БД"""
    global messages
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, phone, message, timestamp, type FROM sms_messages ORDER BY id DESC LIMIT ?", (max_messages,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = [
            {
                "id": row[0],
                "phone": row[1],
                "text": row[2],
                "timestamp": row[3],
                "type": row[4]
            }
            for row in rows
        ]
    except:
        messages = []


def save_to_db(msgs):
    """Зберегти повідомлення в БД"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sms_messages")
        
        for msg in reversed(msgs):
            cursor.execute(
                "INSERT INTO sms_messages (phone, message, timestamp, type) VALUES (?, ?, ?, ?)",
                (msg.get("phone"), msg.get("text"), msg.get("timestamp"), msg.get("type"))
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Помилка BD: {e}")


def on_mqtt_connect(client, userdata, flags, rc):
    """MQTT обробник підключення"""
    if rc == 0:
        print("✓ Підключено до MQTT брокера")
        client.subscribe(SMS_TOPIC)
    else:
        print(f"✗ Помилка підключення, код: {rc}")


def on_mqtt_message(client, userdata, msg):
    """MQTT обробник повідомлень"""
    global messages
    try:
        payload = json.loads(msg.payload.decode())
        
        msg_obj = {
            "id": len(messages) + 1,
            "phone": payload.get("phone", "Unknown"),
            "text": payload.get("message", ""),
            "timestamp": datetime.now().isoformat(),
            "type": "received"
        }
        
        messages.insert(0, msg_obj)
        if len(messages) > max_messages:
            messages.pop()
        
        save_to_db(messages)
        print(f"📨 SMS від {msg_obj['phone']}: {msg_obj['text']}")
    except Exception as e:
        print(f"Помилка обробки повідомлення: {e}")


def get_html_content():
    """Повернути HTML контент"""
    return """<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMS Dashboard - pz-MQTT</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 10px 10px 0 0;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 5px;
            font-size: 28px;
        }
        
        .header p {
            color: #666;
            font-size: 14px;
        }
        
        .content {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .messages-section {
            background: white;
            border-radius: 0 0 10px 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
        }
        
        .messages-header {
            padding: 20px 30px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .messages-header h2 {
            color: #333;
            font-size: 18px;
        }
        
        .btn-clear {
            background: #ff6b6b;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.3s;
        }
        
        .btn-clear:hover {
            background: #ff5252;
        }
        
        .messages-list {
            flex: 1;
            overflow-y: auto;
            max-height: 500px;
            padding: 20px 30px;
        }
        
        .message {
            background: #f9f9f9;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 5px;
            animation: slideIn 0.3s ease-out;
        }
        
        .message.received {
            border-left-color: #4caf50;
        }
        
        .message.sent {
            border-left-color: #2196f3;
            background: #e3f2fd;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(-20px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .message-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 12px;
        }
        
        .phone {
            font-weight: 600;
            color: #333;
        }
        
        .timestamp {
            color: #999;
            font-size: 11px;
        }
        
        .type-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .type-badge.sent {
            background: #2196f3;
            color: white;
        }
        
        .type-badge.received {
            background: #4caf50;
            color: white;
        }
        
        .message-text {
            color: #333;
            word-wrap: break-word;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .empty-state {
            text-align: center;
            color: #999;
            padding: 40px 20px;
        }
        
        .empty-state p {
            font-size: 14px;
        }
        
        /* Права колонка - форма */
        .form-section {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            height: fit-content;
        }
        
        .form-section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 16px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            color: #666;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        input, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 13px;
            font-family: inherit;
            resize: vertical;
        }
        
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        textarea {
            min-height: 80px;
            max-height: 200px;
        }
        
        .btn-send {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            font-size: 14px;
        }
        
        .btn-send:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-send:active {
            transform: translateY(0);
        }
        
        .btn-send:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        .status {
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            margin-top: 10px;
            text-align: center;
            display: none;
        }
        
        .status.success {
            background: #e8f5e9;
            color: #2e7d32;
            display: block;
        }
        
        .status.error {
            background: #ffebee;
            color: #c62828;
            display: block;
        }
        
        .stats {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 5px;
            font-size: 12px;
            color: #666;
            margin-top: 15px;
            text-align: center;
        }
        
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
            
            .messages-list {
                max-height: 300px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 SMS Dashboard</h1>
            <p>pz-MQTT SMS менеджер - відправляйте та розглядайте SMS в реальному часі</p>
        </div>
        
        <div class="content">
            <div class="messages-section">
                <div class="messages-header">
                    <h2>📨 Повідомлення (<span id="count">0</span>)</h2>
                    <button class="btn-clear" onclick="clearMessages()">Очистити</button>
                </div>
                <div class="messages-list" id="messagesList">
                    <div class="empty-state">
                        <p>📭 Повідомлень немає</p>
                    </div>
                </div>
            </div>
            
            <div class="form-section">
                <h3>✉️ Нове СМС</h3>
                
                <div class="form-group">
                    <label for="phone">Номер телефону:</label>
                    <input type="tel" id="phone" placeholder="+380..." value="+380501234567">
                </div>
                
                <div class="form-group">
                    <label for="message">Текст повідомлення:</label>
                    <textarea id="message" placeholder="Введіть текст СМС...">Привіт! Це тестове СМС</textarea>
                </div>
                
                <button class="btn-send" onclick="sendSMS()">Надіслати СМС</button>
                
                <div id="status" class="status"></div>
                
                <div class="stats">
                    <p>🟢 Онлайн</p>
                    <p>Брокер: MQTT</p>
                    <p id="lastUpdate">Оновлено: --:--</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        console.log("📱 SMS Dashboard завантажується...");
        console.log("🔗 Підключення до сервера на http://localhost:8000");
        
        // Регулярно завантажувати повідомлення
        async function loadMessages() {
            try {
                const response = await fetch("/api/messages");
                const data = await response.json();
                
                console.log(`📥 Завантажено ${data.length} повідомлень`, data);
                
                displayMessages(data);
                updateLastUpdate();
            } catch (error) {
                console.error("❌ Помилка завантаження повідомлень:", error);
            }
        }
        
        function displayMessages(msgs) {
            const listEl = document.getElementById("messagesList");
            const countEl = document.getElementById("count");
            
            countEl.textContent = msgs.length;
            
            if (msgs.length === 0) {
                console.log("📭 Повідомлень немає");
                listEl.innerHTML = '<div class="empty-state"><p>📭 Повідомлень немає</p></div>';
                return;
            }
            
            // Детальне логування кожного СМС
            msgs.forEach((msg, index) => {
                const icon = msg.type === 'sent' ? '📤' : '📥';
                const type = msg.type === 'sent' ? 'ВІДПРАВЛЕНО' : 'ОТРИМАНО';
                
                console.group(`${icon} СМС #${index + 1} [${type}]`);
                console.log("📞 Номер:", msg.phone);
                console.log("💬 Текст:", msg.text);
                console.log("⏰ Час:", new Date(msg.timestamp).toLocaleString('uk-UA'));
                console.log("🔑 ID:", msg.id);
                console.log("📊 Повний об'єкт:", msg);
                console.groupEnd();
            });
            
            listEl.innerHTML = msgs.map(msg => `
                <div class="message ${msg.type}">
                    <div class="message-header">
                        <span class="phone">${msg.phone}</span>
                        <span>
                            <span class="timestamp">${new Date(msg.timestamp).toLocaleString('uk-UA')}</span>
                            <span class="type-badge ${msg.type}">${msg.type === 'sent' ? '📤 Відправлено' : '📥 Отримано'}</span>
                        </span>
                    </div>
                    <div class="message-text">${escapeHtml(msg.text)}</div>
                </div>
            `).join("");
        }
        
        async function sendSMS() {
            const phone = document.getElementById("phone").value.trim();
            const message = document.getElementById("message").value.trim();
            const statusEl = document.getElementById("status");
            const btnSend = document.querySelector(".btn-send");
            
            console.group("📤 Відправка нового СМС");
            console.log("📞 Номер:", phone);
            console.log("💬 Текст:", message);
            
            if (!phone || !message) {
                console.warn("⚠️ Номер або текст не заповнені!");
                console.groupEnd();
                showStatus("Заповніть номер та текст повідомлення!", "error");
                return;
            }
            
            btnSend.disabled = true;
            
            try {
                console.log("🔄 Відправка запиту на сервер...");
                
                const response = await fetch("/api/send-sms", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({phone, message})
                });
                
                console.log("📡 Статус відповіді сервера:", response.status);
                
                if (response.ok) {
                    const result = await response.json();
                    console.log("✅ СМС успішно надіслано!", result);
                    console.log("🆔 ID повідомлення:", result.id);
                    console.groupEnd();
                    
                    showStatus("✓ СМС надіслано!", "success");
                    document.getElementById("message").value = "";
                    await new Promise(r => setTimeout(r, 500));
                    loadMessages();
                } else {
                    console.error("❌ Помилка при відправці СМС. Статус:", response.status);
                    console.groupEnd();
                    showStatus("Помилка при відправці СМС", "error");
                }
            } catch (error) {
                console.error("❌ Критична помилка:", error);
                console.groupEnd();
                showStatus("Помилка: " + error.message, "error");
            } finally {
                btnSend.disabled = false;
            }
        }
        
        async function clearMessages() {
            if (!confirm("Видалити всі повідомлення?")) {
                console.log("⚠️ Очистка скасована користувачем");
                return;
            }
            
            console.log("🗑️ Очистка всіх повідомлень...");
            
            try {
                const response = await fetch("/api/clear", {method: "POST"});
                console.log("✅ Повідомлення очищені. Статус:", response.status);
                loadMessages();
            } catch (error) {
                console.error("❌ Помилка при очистці:", error);
            }
        }
        
        function showStatus(message, type) {
            const statusEl = document.getElementById("status");
            statusEl.textContent = message;
            statusEl.className = "status " + type;
            
            const icon = type === 'success' ? '✅' : '❌';
            console.log(`${icon} ${message}`);
            
            setTimeout(() => statusEl.className = "status", 3000);
        }
        
        function escapeHtml(text) {
            return text.replace(/[&<>"']/g, m => ({
                "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
            })[m]);
        }
        
        function updateLastUpdate() {
            const now = new Date();
            document.getElementById("lastUpdate").textContent = 
                "Оновлено: " + now.toLocaleTimeString('uk-UA');
        }
        
        // Ініціалізація
        console.log("═══════════════════════════════════════");
        console.log("🚀 SMS Dashboard запущений");
        console.log("═══════════════════════════════════════");
        console.log("💡 Порада: Всі события будуть показані тут в консолі");
        console.log("🔑 Скорочення: F12 або Ctrl+Shift+I для відкриття консолі");
        console.log("═══════════════════════════════════════");
        
        loadMessages();
        setInterval(loadMessages, 2000);
    </script>
</body>
</html>
"""


def start_mqtt_client():
    """Запустити MQTT клієнт"""
    global mqtt_client
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="sms-dashboard")
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"✗ Помилка підключення до MQTT: {e}")


def start_web_server():
    """Запустити веб-сервер"""
    server = ThreadingHTTPServer(("0.0.0.0", WEB_PORT), SMSRequestHandler)
    print(f"\n🌐 Веб-сервер запущений на http://localhost:{WEB_PORT}")
    print("   Відкрийте браузер та перейдіть за цією адресою\n")
    server.serve_forever()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("📱 MQTT SMS Dashboard")
    print("="*60 + "\n")
    
    # Ініціалізація БД
    init_database()
    load_from_db()
    
    # Запустити MQTT
    mqtt_client = None
    mqtt_thread = threading.Thread(target=start_mqtt_client, daemon=True)
    mqtt_thread.start()
    
    # Запустити веб-сервер
    try:
        start_web_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Сервер зупинений")
        if mqtt_client:
            mqtt_client.loop_stop()
