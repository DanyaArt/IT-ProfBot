from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = "8904132865:AAFSrkvUzj9OJ3xs3gH_UwbABIi0-mDYRVs"

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

def get_main_keyboard():
    return {
        "keyboard": [
            [{"text": "Начать тест"}],
            [{"text": "Помощь"}]
        ],
        "resize_keyboard": True
    }

@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        
        if text == '/start':
            send_message(chat_id, "🎓 Добро пожаловать!\n\nНажмите 'Начать тест'", get_main_keyboard())
        elif text == 'Начать тест':
            send_message(chat_id, "✅ Тест начат! Отвечайте на вопросы.")
        elif text == 'Помощь':
            send_message(chat_id, "Нажмите 'Начать тест' для начала")
        else:
            send_message(chat_id, f"Вы ответили: {text}\n\nПродолжайте тест!")
    
    return jsonify({"ok": True})

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
