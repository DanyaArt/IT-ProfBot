from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = "8904132865:AAFSrkvUzj9OJ3xs3gH_UwbABIi0-mDYRVs"

# Это главный и единственный обработчик
@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        # Бот просто отвечает "Привет!" на любое сообщение
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        payload = {'chat_id': chat_id, 'text': 'Привет! Я бот и я работаю!'}
        requests.post(url, json=payload)
    return jsonify({"ok": True})

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)