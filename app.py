import threading
import time
import os

# Запускаем оригинального бота в отдельном потоке
def run_bot():
    # Импортируем и запускаем оригинального бота
    import fixed_bot

# Запускаем бота в фоне
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()

# Flask сервер для Render (чтобы не убили процесс)
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running! Original bot is working in background."

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    # Получаем порт из окружения Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
