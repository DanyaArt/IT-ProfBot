from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

BOT_TOKEN = "8904132865:AAFSrkvUzj9OJ3xs3gH_UwbABIi0-mDYRVs"

# 30 вопросов (категории: code, data, design, security, devops, mobile, game, ai_ml)
QUESTIONS = [
    {"text": "Вам нравится решать логические задачи и головоломки?", "cat": "code"},
    {"text": "Вы предпочитаете работать с цифрами и статистикой?", "cat": "data"},
    {"text": "Вам интересно создавать красивые интерфейсы и макеты?", "cat": "design"},
    {"text": "Вы задумываетесь о безопасности данных и защите от взломов?", "cat": "security"},
    {"text": "Вам нравится автоматизировать рутинные процессы?", "cat": "devops"},
    {"text": "Вы интересуетесь созданием мобильных приложений?", "cat": "mobile"},
    {"text": "Вам интересна разработка игр и 3D-графика?", "cat": "game"},
    {"text": "Вы хотите создавать нейросети и AI-системы?", "cat": "ai_ml"},
    {"text": "Вы любите разбираться в чужом коде и находить ошибки?", "cat": "code"},
    {"text": "Вам нравится искать закономерности в больших данных?", "cat": "data"},
    {"text": "Вы обращаете внимание на удобство использования сайтов?", "cat": "design"},
    {"text": "Вам интересно тестировать системы на прочность?", "cat": "security"},
    {"text": "Вы хотите настраивать серверы и облачные системы?", "cat": "devops"},
    {"text": "Вам нравится разрабатывать приложения для телефонов?", "cat": "mobile"},
    {"text": "Вы мечтаете создавать свои игры?", "cat": "game"},
    {"text": "Вас привлекает машинное обучение и нейросети?", "cat": "ai_ml"},
    {"text": "Вы хорошо пишете алгоритмы и оптимизируете код?", "cat": "code"},
    {"text": "Вам нравится визуализировать данные?", "cat": "data"},
    {"text": "Вы цените эстетику и внимание к деталям?", "cat": "design"},
    {"text": "Вам интересна криптография и сетевые протоколы?", "cat": "security"},
    {"text": "Вы хотите автоматизировать развертывание приложений?", "cat": "devops"},
    {"text": "Вам нравится создавать кросс-платформенные приложения?", "cat": "mobile"},
    {"text": "Вы хотите разрабатывать игры на Unity?", "cat": "game"},
    {"text": "Вас вдохновляет создание умных помощников?", "cat": "ai_ml"},
    {"text": "Вы умеете писать чистый и понятный код?", "cat": "code"},
    {"text": "Вам нравится работать с SQL и базами данных?", "cat": "data"},
    {"text": "Вы следите за трендами в веб-дизайне?", "cat": "design"},
    {"text": "Вам интересно искать уязвимости в системах?", "cat": "security"},
    {"text": "Вы хотите работать с Docker и Kubernetes?", "cat": "devops"},
    {"text": "Вас привлекает создание приложений для миллионов?", "cat": "mobile"}
]

OPTIONS = [
    {"text": "✅ Да", "score": 3},
    {"text": "🤔 Скорее да", "score": 2},
    {"text": "🙁 Скорее нет", "score": 1},
    {"text": "❌ Нет", "score": 0}
]

SPEC_MAP = {
    "code": "Программная инженерия",
    "data": "Data Science",
    "design": "UX/UI дизайн",
    "security": "Кибербезопасность",
    "devops": "DevOps инженерия",
    "mobile": "Мобильная разработка",
    "game": "Game Development",
    "ai_ml": "AI/ML инженерия"
}

user_sessions = {}

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

def get_main_keyboard():
    return {"keyboard": [[{"text": "Начать тест"}], [{"text": "Помощь"}]], "resize_keyboard": True}

def get_question_keyboard():
    return {"keyboard": [[{"text": o["text"]}] for o in OPTIONS], "resize_keyboard": True}

def send_question(chat_id, user_id, q_num):
    if q_num > len(QUESTIONS):
        # Показываем результаты
        scores = user_sessions[user_id]["scores"]
        total = sum(scores.values())
        if total > 0:
            percentages = {cat: int((v/total)*100) for cat, v in scores.items()}
        else:
            percentages = {cat: 0 for cat in scores}
        max_cat = max(scores, key=scores.get)
        result = f"🎉 <b>Тест завершен!</b>\n\n📊 Результаты:\n"
        for cat, name in SPEC_MAP.items():
            result += f"• {name}: {percentages.get(cat, 0)}%\n"
        result += f"\n🎯 <b>Рекомендуемая специализация:</b>\n<b>{SPEC_MAP[max_cat]}</b>\n\nНажмите /start для нового теста"
        send_message(chat_id, result, get_main_keyboard())
        del user_sessions[user_id]
        return
    
    q = QUESTIONS[q_num - 1]
    text = f"❓ <b>Вопрос {q_num}/{len(QUESTIONS)}</b>\n\n{q['text']}"
    send_message(chat_id, text, get_question_keyboard())

@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"ok": True})
    
    msg = data['message']
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    text = msg.get('text', '')
    
    if text == '/start':
        if user_id in user_sessions:
            del user_sessions[user_id]
        send_message(chat_id, "🎓 Добро пожаловать!\n\nНажмите 'Начать тест'", get_main_keyboard())
    elif text == 'Начать тест':
        if user_id in user_sessions:
            del user_sessions[user_id]
        user_sessions[user_id] = {"current": 1, "scores": {cat: 0 for cat in SPEC_MAP}}
        send_question(chat_id, user_id, 1)
    elif text == 'Помощь':
        send_message(chat_id, "Нажмите 'Начать тест' для прохождения теста (30 вопросов)", get_main_keyboard())
    elif user_id in user_sessions:
        session = user_sessions[user_id]
        current = session["current"]
        if current <= len(QUESTIONS):
            for opt in OPTIONS:
                if opt["text"] == text:
                    cat = QUESTIONS[current-1]["cat"]
                    session["scores"][cat] += opt["score"]
                    break
            session["current"] += 1
            send_question(chat_id, user_id, session["current"])
        else:
            send_question(chat_id, user_id, current)
    else:
        send_message(chat_id, "Нажмите 'Начать тест'", get_main_keyboard())
    
    return jsonify({"ok": True})

@app.route('/')
def index():
    return "Bot is running with 30 questions!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
