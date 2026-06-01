from flask import Flask, request, jsonify
import requests
import json
from config import Config
from database.queries import Database

app = Flask(__name__)

BOT_TOKEN = Config.BOT_TOKEN
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

db = Database(Config.DB_URL)
user_sessions = {}

def send_message(chat_id, text, reply_markup=None):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(url, json=payload, timeout=30)
    except Exception as e:
        print(f"Ошибка: {e}")

def get_main_keyboard():
    return {"keyboard": [[{"text": "Начать тест"}], [{"text": "Помощь"}]], "resize_keyboard": True}

@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"ok": True})
    
    msg = data['message']
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    text = msg.get('text', '')
    
    print(f"📨 {user_id}: {text}")
    
    if text == '/start':
        send_message(chat_id, "🎓 Добро пожаловать в IT-профориентатор!\n\nНажмите 'Начать тест'", get_main_keyboard())
    elif text == 'Начать тест':
        send_message(chat_id, "✅ Тест начат! (Полная версия с 30 вопросами будет добавлена позже)")
    elif text == 'Помощь':
        send_message(chat_id, "Нажмите 'Начать тест' для начала тестирования", get_main_keyboard())
    else:
        send_message(chat_id, "Нажмите 'Начать тест' для начала", get_main_keyboard())
    
    return jsonify({"ok": True})

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
