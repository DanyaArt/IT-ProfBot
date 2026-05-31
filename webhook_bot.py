from flask import Flask, request, jsonify
import requests
import json
import os
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


def get_question_keyboard(options):
    keyboard = [[{"text": opt['text'] if isinstance(opt, dict) else opt}] for opt in options]
    return {"keyboard": keyboard, "resize_keyboard": True}


def send_question(chat_id, user_id, q_num):
    all_q = db.get_all_questions()
    if not all_q:
        return
    q_ids = sorted(all_q.keys())
    if q_num > len(q_ids):
        show_results(chat_id, user_id)
        return
    q_id = q_ids[q_num - 1]
    q = all_q[q_id]
    markup = get_question_keyboard(q['options'])
    text = f"❓ Вопрос {q_num}/{len(q_ids)}\n\n{q['text']}"
    send_message(chat_id, text, markup)


def show_results(chat_id, user_id):
    session = user_sessions.get(user_id)
    if not session:
        return
    scores = {"code": 0, "data": 0, "design": 0, "security": 0, "devops": 0, "mobile": 0, "game": 0, "ai_ml": 0}
    all_q = db.get_all_questions()
    q_ids = sorted(all_q.keys())
    for i, q_id in enumerate(q_ids, 1):
        if str(i) in session.get('answers', {}):
            val = session['answers'][str(i)]
            q = all_q[q_id]
            for opt in q['options']:
                if isinstance(opt, dict) and opt.get('value') == val:
                    cat = opt.get('category', 'code')
                    if cat in scores:
                        scores[cat] += val
                    break
    spec_map = {"code": "Программная инженерия", "data": "Data Science", "design": "UX/UI дизайн",
                "security": "Кибербезопасность", "devops": "DevOps инженерия", "mobile": "Мобильная разработка",
                "game": "Game Development", "ai_ml": "AI/ML инженерия"}
    max_cat = max(scores, key=scores.get) if max(scores.values()) > 0 else "code"
    result = f"🎉 Тест завершен!\n\n🎯 Специализация: {spec_map[max_cat]}\n\n📊 Результаты:\n• Программирование: {scores['code']}\n• Анализ данных: {scores['data']}\n• Дизайн: {scores['design']}\n• Безопасность: {scores['security']}"
    send_message(chat_id, result, get_main_keyboard())
    del user_sessions[user_id]


@app.route(f"/webhook/{BOT_TOKEN}", methods=['POST'])
def webhook():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"ok": True})

    msg = data['message']
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    text = msg.get('text', '')

    if text == '/start' or text == 'Начать тест':
        if user_id in user_sessions:
            del user_sessions[user_id]
        user_sessions[user_id] = {'current': 1, 'answers': {}}
        send_question(chat_id, user_id, 1)
    elif text == 'Помощь':
        send_message(chat_id, "Нажмите 'Начать тест'", get_main_keyboard())
    elif user_id in user_sessions:
        session = user_sessions[user_id]
        all_q = db.get_all_questions()
        q_ids = sorted(all_q.keys())
        if session['current'] <= len(q_ids):
            q_id = q_ids[session['current'] - 1]
            q = all_q[q_id]
            valid = [opt['text'] if isinstance(opt, dict) else opt for opt in q['options']]
            if text in valid:
                for opt in q['options']:
                    if (isinstance(opt, dict) and opt['text'] == text) or opt == text:
                        val = opt.get('value', 0) if isinstance(opt, dict) else 0
                        session['answers'][str(session['current'])] = val
                        break
                session['current'] += 1
                send_question(chat_id, user_id, session['current'])
            else:
                send_message(chat_id, "❌ Выберите вариант из кнопок")
                send_question(chat_id, user_id, session['current'])
    else:
        send_message(chat_id, "Нажмите 'Начать тест'", get_main_keyboard())

    return jsonify({"ok": True})


@app.route('/')
def index():
    return "Bot is running!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)