#!/usr/bin/env python3
"""
Simple MQTT Broker using Aedes-like implementation
This is a basic MQTT broker for testing purposes
"""

import socket
import threading
import struct
import time
from collections import defaultdict

class SimpleMQTTBroker:
    def __init__(self, host='localhost', port=1883):
        self.host = host
        self.port = port
        self.clients = {}
        self.subscriptions = defaultdict(set)
        self.messages = defaultdict(list)
        self.server_socket = None
        self.running = False
        
    def start(self):
        """Start the MQTT broker"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"🚀 MQTT Broker запущений на {self.host}:{self.port}")
        print("=" * 50)
        print("✅ Брокер готовий до прийому підключень")
        print("=" * 50)
        print("\nСтандартні налаштування:")
        print("  - Порт: 1883 (MQTT)")
        print("  - Анонімні підключення: Дозволені")
        print("  - Max clients: Невизначено")
        print("\n📌 Топіки для тестування:")
        print("  - test/topic")
        print("  - sensor/temperature")
        print("  - sensor/humidity")
        print("  - device/status")
        print("\n" + "=" * 50)
        
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"\n✓ Новий клієнт підключився: {address}")
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
            except KeyboardInterrupt:
                print("\n\n🛑 Брокер зупинено...")
                self.stop()
                break
            except Exception as e:
                if self.running:
                    print(f"Помилка при прийманні підключення: {e}")
    
    def handle_client(self, client_socket, address):
        """Handle individual client connections"""
        try:
            client_id = f"client_{address[1]}"
            self.clients[client_id] = {
                'socket': client_socket,
                'address': address,
                'subscribed_topics': set()
            }
            
            # Simple handshake
            data = client_socket.recv(1024)
            if data:
                print(f"  → {client_id} авторизований")
                
                # Send acknowledgment
                response = b'\x20\x02\x00\x00'  # CONNACK
                client_socket.send(response)
                
                # Listen for messages
                while self.running:
                    try:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        
                        # Simple message handling
                        if len(data) > 4:
                            msg_type = (data[0] >> 4) & 0x0f
                            
                            if msg_type == 3:  # PUBLISH
                                topic, message = self.parse_publish(data)
                                if topic:
                                    print(f"  📤 {client_id} опублікував '{message}' в '{topic}'")
                                    self.broadcast_message(topic, message, client_id)
                            elif msg_type == 8:  # SUBSCRIBE
                                topics = self.parse_subscribe(data)
                                for topic in topics:
                                    self.subscriptions[topic].add(client_id)
                                    self.clients[client_id]['subscribed_topics'].add(topic)
                                    print(f"  📥 {client_id} підписався на '{topic}'")
                                
                                # Send SUBACK
                                suback = b'\x90\x03\x00\x01\x00'
                                client_socket.send(suback)
                            elif msg_type == 14:  # DISCONNECT
                                print(f"  ← {client_id} відключився")
                                break
                    except:
                        break
        except Exception as e:
            print(f"Помилка з клієнтом {address}: {e}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
            client_socket.close()
    
    def parse_publish(self, data):
        """Parse PUBLISH message"""
        try:
            # Skip header and length
            idx = 1
            while idx < len(data) and (data[idx] & 0x80):
                idx += 1
            idx += 1
            
            if idx >= len(data):
                return None, None
            
            # Parse topic length
            topic_len = (data[idx] << 8) | data[idx + 1]
            idx += 2
            
            topic = data[idx:idx + topic_len].decode('utf-8', errors='ignore')
            idx += topic_len
            
            # Parse message
            message = data[idx:].decode('utf-8', errors='ignore')
            
            return topic, message
        except:
            return None, None
    
    def parse_subscribe(self, data):
        """Parse SUBSCRIBE message"""
        try:
            topics = []
            idx = 2  # Skip packet type and flags
            while idx < len(data):
                if idx + 1 >= len(data):
                    break
                topic_len = (data[idx] << 8) | data[idx + 1]
                idx += 2
                if idx + topic_len > len(data):
                    break
                topic = data[idx:idx + topic_len].decode('utf-8', errors='ignore')
                topics.append(topic)
                idx += topic_len + 1  # +1 for QoS
            return topics
        except:
            return []
    
    def broadcast_message(self, topic, message, sender_id):
        """Broadcast message to all subscribers of a topic"""
        if topic in self.subscriptions:
            for client_id in self.subscriptions[topic]:
                if client_id != sender_id and client_id in self.clients:
                    try:
                        # Simple message format
                        msg = f"{topic}:{message}".encode('utf-8')
                        self.clients[client_id]['socket'].send(msg)
                    except:
                        pass
    
    def stop(self):
        """Stop the broker"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("MQTT Broker (Eclipse Mosquitto аналог)")
    print("=" * 50 + "\n")
    
    broker = SimpleMQTTBroker(host='127.0.0.1', port=1883)
    broker.start()
