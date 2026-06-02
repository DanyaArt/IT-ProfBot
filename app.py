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

def get_question_keyboard(options):
    keyboard = []
    for opt in options:
        text = opt['text'] if isinstance(opt, dict) else opt
        keyboard.append([{"text": text}])
    return {"keyboard": keyboard, "resize_keyboard": True}

def send_question(chat_id, user_id, q_num):
    all_q = db.get_all_questions()
    if not all_q:
        send_message(chat_id, "❌ Вопросы не найдены", get_main_keyboard())
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
    answers = session.get('answers', {})
    scores = {"code": 0, "data": 0, "design": 0, "security": 0, "devops": 0, "mobile": 0, "game": 0, "ai_ml": 0}
    all_q = db.get_all_questions()
    q_ids = sorted(all_q.keys())
    for i, q_id in enumerate(q_ids, 1):
        if str(i) in answers:
            val = answers[str(i)]
            q = all_q[q_id]
            for opt in q['options']:
                if isinstance(opt, dict) and opt.get('value') == val:
                    cat = opt.get('category', 'code')
                    if cat in scores:
                        scores[cat] += val
                    break
    total_score = sum(scores.values())
    if total_score > 0:
        percentages = {k: int((v / total_score) * 100) for k, v in scores.items()}
    else:
        percentages = {k: 0 for k in scores}
    max_cat = max(scores, key=scores.get) if max(scores.values()) > 0 else "code"
    spec_map = {"code": "Программная инженерия", "data": "Data Science", "design": "UX/UI дизайн", "security": "Кибербезопасность", "devops": "DevOps инженерия", "mobile": "Мобильная разработка", "game": "Game Development", "ai_ml": "AI/ML инженерия"}
    specialization = spec_map.get(max_cat, "Программная инженерия")
    result_text = f"""
🎉 <b>Тест завершен!</b>

📊 <b>Ваши результаты:</b>
• Программная инженерия: {percentages.get('code', 0)}%
• Data Science: {percentages.get('data', 0)}%
• UX/UI дизайн: {percentages.get('design', 0)}%
• Кибербезопасность: {percentages.get('security', 0)}%
• DevOps инженерия: {percentages.get('devops', 0)}%
• Мобильная разработка: {percentages.get('mobile', 0)}%
• Game Development: {percentages.get('game', 0)}%
• AI/ML инженерия: {percentages.get('ai_ml', 0)}%

🎯 <b>Рекомендуемая специализация:</b>
<b>{specialization}</b>

💡 <b>Что дальше?</b>
• Изучайте актуальные технологии
• Собирайте портфолио
• Проходите стажировки

Нажмите /start для нового теста
"""
    send_message(chat_id, result_text, get_main_keyboard())
    if user_id in user_sessions:
        del user_sessions[user_id]

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
        if user_id in user_sessions:
            del user_sessions[user_id]
        send_message(chat_id, "🎓 Добро пожаловать в IT-профориентатор!\n\nНажмите 'Начать тест'", get_main_keyboard())
        return jsonify({"ok": True})
    
    if text == 'Начать тест':
        if user_id in user_sessions:
            del user_sessions[user_id]
        user_sessions[user_id] = {'current': 1, 'answers': {}}
        send_question(chat_id, user_id, 1)
        return jsonify({"ok": True})
    
    if text == 'Помощь':
        send_message(chat_id, "Нажмите 'Начать тест' для прохождения теста", get_main_keyboard())
        return jsonify({"ok": True})
    
    if user_id in user_sessions:
        session = user_sessions[user_id]
        all_q = db.get_all_questions()
        if not all_q:
            return jsonify({"ok": True})
        q_ids = sorted(all_q.keys())
        current_q = session.get('current', 1)
        if current_q <= len(q_ids):
            q_id = q_ids[current_q - 1]
            q = all_q[q_id]
            valid = [opt['text'] if isinstance(opt, dict) else opt for opt in q['options']]
            if text in valid:
                for opt in q['options']:
                    opt_text = opt['text'] if isinstance(opt, dict) else opt
                    if opt_text == text:
                        val = opt.get('value', 0) if isinstance(opt, dict) else 0
                        session['answers'][str(current_q)] = val
                        break
                session['current'] = current_q + 1
                send_question(chat_id, user_id, session['current'])
            else:
                send_question(chat_id, user_id, current_q)
        else:
            show_results(chat_id, user_id)
        return jsonify({"ok": True})
    
    send_message(chat_id, "Нажмите 'Начать тест' для начала", get_main_keyboard())
    return jsonify({"ok": True})

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
