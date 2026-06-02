from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = "8904132865:AAFSrkvUzj9OJ3xs3gH_UwbABIi0-mDYRVs"

# Хранилище ответов пользователей
user_sessions = {}

# 30 вопросов с категориями
QUESTIONS = [
    {"text": "Вам нравится решать логические задачи и головоломки?", "category": "code"},
    {"text": "Вы предпочитаете работать с цифрами и статистикой?", "category": "data"},
    {"text": "Вам интересно создавать красивые интерфейсы и макеты?", "category": "design"},
    {"text": "Вы задумываетесь о безопасности данных и защите от взломов?", "category": "security"},
    {"text": "Вам нравится автоматизировать рутинные процессы?", "category": "devops"},
    {"text": "Вы интересуетесь созданием мобильных приложений?", "category": "mobile"},
    {"text": "Вам интересна разработка игр и 3D-графика?", "category": "game"},
    {"text": "Вы хотите создавать нейросети и AI-системы?", "category": "ai_ml"},
    {"text": "Вы любите разбираться в чужом коде и находить ошибки?", "category": "code"},
    {"text": "Вам нравится искать закономерности в больших данных?", "category": "data"},
    {"text": "Вы обращаете внимание на удобство использования сайтов и приложений?", "category": "design"},
    {"text": "Вам интересно тестировать системы на прочность?", "category": "security"},
    {"text": "Вы хотите настраивать серверы и облачные инфраструктуры?", "category": "devops"},
    {"text": "Вам нравится разрабатывать приложения для iOS или Android?", "category": "mobile"},
    {"text": "Вы мечтаете создавать свои игры?", "category": "game"},
    {"text": "Вас привлекает машинное обучение и анализ данных?", "category": "ai_ml"},
    {"text": "Вы хорошо пишете алгоритмы и оптимизируете код?", "category": "code"},
    {"text": "Вам нравится визуализировать данные и делать дашборды?", "category": "data"},
    {"text": "Вы цените эстетику и внимание к деталям в дизайне?", "category": "design"},
    {"text": "Вам интересна криптография и сетевые протоколы?", "category": "security"},
    {"text": "Вы хотите автоматизировать развертывание приложений (CI/CD)?", "category": "devops"},
    {"text": "Вам нравится создавать кроссплатформенные приложения?", "category": "mobile"},
    {"text": "Вы хотите разрабатывать игры на Unity или Unreal Engine?", "category": "game"},
    {"text": "Вас вдохновляет создание умных помощников и чат-ботов?", "category": "ai_ml"},
    {"text": "Вы умеете писать чистый и понятный код?", "category": "code"},
    {"text": "Вам нравится работать с SQL и базами данных?", "category": "data"},
    {"text": "Вы следите за трендами в веб-дизайне?", "category": "design"},
    {"text": "Вам интересно искать уязвимости в системах?", "category": "security"},
    {"text": "Вы хотите работать с Docker и Kubernetes?", "category": "devops"},
    {"text": "Вас привлекает создание приложений для миллионов пользователей?", "category": "mobile"}
]

# Варианты ответов (все вопросы имеют одинаковые варианты)
OPTIONS = [
    {"text": "✅ Да, очень нравится", "score": 3},
    {"text": "🤔 Скорее да, чем нет", "score": 2},
    {"text": "🙁 Скорее нет, чем да", "score": 1},
    {"text": "❌ Нет, не нравится", "score": 0}
]

def get_question_keyboard():
    keyboard = [[{"text": opt["text"]}] for opt in OPTIONS]
    return {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}

def get_main_menu():
    return {"keyboard": [[{"text": "Начать тест"}], [{"text": "Помощь"}]], "resize_keyboard": True}

def get_result_keyboard():
    return {"keyboard": [[{"text": "Начать тест"}], [{"text": "Помощь"}]], "resize_keyboard": True}

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=30)
    except Exception as e:
        print(f"Ошибка: {e}")

def send_question(chat_id, user_id, q_num):
    if q_num > len(QUESTIONS):
        show_results(chat_id, user_id)
        return
    
    q = QUESTIONS[q_num - 1]
    text = f"❓ <b>Вопрос {q_num}/{len(QUESTIONS)}</b>\n\n{q['text']}"
    send_message(chat_id, text, get_question_keyboard())

def show_results(chat_id, user_id):
    if user_id not in user_sessions:
        return
    
    scores = user_sessions[user_id]["scores"]
    
    # Специализации и их вес
    categories = {
        "code": "Программная инженерия",
        "data": "Data Science",
        "design": "UX/UI дизайн",
        "security": "Кибербезопасность",
        "devops": "DevOps инженерия",
        "mobile": "Мобильная разработка",
        "game": "Game Development",
        "ai_ml": "AI/ML инженерия"
    }
    
    # Подсчёт процентов
    total_score = sum(scores.values())
    if total_score == 0:
        percentages = {cat: 0 for cat in categories}
    else:
        percentages = {cat: int((scores[cat] / total_score) * 100) for cat in categories}
    
    # Определяем максимальную категорию
    max_cat = max(scores, key=scores.get) if max(scores.values()) > 0 else "code"
    specialization = categories[max_cat]
    
    # Формируем результат
    result = f"""
🎉 <b>Тест завершен!</b>

📊 <b>Ваши результаты по направлениям:</b>
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
• Изучайте актуальные технологии в выбранной сфере
• Собирайте портфолио проектов
• Проходите стажировки

Нажмите /start для нового теста
"""
    send_message(chat_id, result, get_result_keyboard())
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
    
    # Команда /start
    if text == '/start':
        if user_id in user_sessions:
            del user_sessions[user_id]
        send_message(chat_id, "🎓 <b>Добро пожаловать в IT-профориентатор!</b>\n\nЭтот бот поможет определить подходящую IT-специализацию.\n\n📋 Тест содержит 30 вопросов и займет ~10 минут.\n\nНажмите 'Начать тест'!", get_main_menu())
        return jsonify({"ok": True})
    
    # Кнопка "Начать тест"
    if text == 'Начать тест':
        if user_id in user_sessions:
            del user_sessions[user_id]
        user_sessions[user_id] = {"current": 1, "scores": {cat: 0 for cat in ["code", "data", "design", "security", "devops", "mobile", "game", "ai_ml"]}}
        send_question(chat_id, user_id, 1)
        return jsonify({"ok": True})
    
    # Кнопка "Помощь"
    if text == 'Помощь':
        send_message(chat_id, "📚 <b>Помощь</b>\n\n• Начать тест - запустить тестирование\n• /start - начать заново\n\nТест содержит 30 вопросов. Отвечайте честно!", get_main_menu())
        return jsonify({"ok": True})
    
    # Если пользователь в процессе теста
    if user_id in user_sessions:
        session = user_sessions[user_id]
        current = session["current"]
        
        if current <= len(QUESTIONS):
            # Проверяем, что ответ правильный
            valid_answers = [opt["text"] for opt in OPTIONS]
            if text in valid_answers:
                # Находим выбранный вариант и добавляем баллы
                for opt in OPTIONS:
                    if opt["text"] == text:
                        category = QUESTIONS[current - 1]["category"]
                        session["scores"][category] += opt["score"]
                        break
                session["current"] += 1
                send_question(chat_id, user_id, session["current"])
            else:
                send_message(chat_id, "❌ Пожалуйста, выберите вариант из кнопок", get_question_keyboard())
        else:
            show_results(chat_id, user_id)
        return jsonify({"ok": True})
    
    # Если ничего не подошло
    send_message(chat_id, "Нажмите 'Начать тест' для начала", get_main_menu())
    return jsonify({"ok": True})

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
