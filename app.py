from flask import Flask, request, jsonify
import subprocess
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

# Импортируем и запускаем оригинального бота
import fixed_bot

app = Flask(__name__)

# Этот эндпоинт нужен для проверки работы сервера
@app.route('/')
def index():
    return "Bot is running! Original bot is working in background."

# Запускаем оригинального бота в отдельном процессе
if __name__ == '__main__':
    # Запускаем fixed_bot.py в фоне
    import threading
    def run_bot():
        exec(open('fixed_bot.py').read())
    
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=10000)
