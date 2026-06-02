from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = "8904132865:AAFSrkvUzj9OJ3xs3gH_UwbABIi0-mDYRVs"

# Хранилище ответов пользователей
user_sessions = {}

# Вопросы: текст вопроса и варианты ответов с баллами
QUESTIONS = [
    {
        "text": "Что вам больше нравится?",
        "options": [
            {"text": "Писать код", "score": 3},
            {"text": "Анализировать данные", "score": 2},
            {"text": "Рисовать дизайн", "score": 1},
            {"text": "Настраивать безопасность", "score": 2}
        ]
    },
    {
        "text": "Как вы решаете проблемы?",
        "options": [
            {"text": "Логически и последовательно", "score": 3},
            {"text": "Интуитивно и творчески", "score": 1},
            {"text": "Исследуя данные", "score": 2},
            {"text": "Ищу уязвимости", "score": 2}
        ]
    },
    {
        "text": "Что вас привлекает в IT?",
        "options": [
            {"text": "Создавать новые продукты", "score": 3},
            {"text": "Понимать как работают системы", "score": 2},
            {"text": "Делать интерфейсы красивыми", "score": 1},
            {"text": "Защищать от взломов", "score": 2}
        ]
    },
    {
        "text": "Выберите стиль работы:",
        "options": [
            {"text": "Индивидуально и глубоко", "score": 2},
            {"text": "В команде над проектом", "score": 3},
            {"text": "Свободный график", "score": 1},
            {"text": "Строгий регламент", "score": 2}
        ]
    },
    {
        "text": "Что важнее для вас?",
        "options": [
            {"text": "Функциональность", "score": 3},
            {"text": "Безопасность", "score": 2},
            {"text": "Внешний вид", "score": 1},
            {"text": "Производительность", "score": 2}
        ]
    }
]

# Клавиатура с вариантами ответов
def get_question_keyboard(options):
    keyboard = [[{"text": opt["text"]}] for opt in options]
    return {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True}

# Обычное меню
def get_main_menu():
    return {"keyboard": [[{"text": "Начать тест"}], [{"text": "Помощ�"}]], "resize_keyboard": True}

# Отправить сообщение
def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=30)
    except Exception as e:
        print(f"Ошибка: {e}")

# Отправить вопрос
def send_question(chat_id, user_id, q_num):
    if q_num > len(QUESTIONS):
        # Тест закончен — показываем результат
        scores = user_sessions[user_id]["scores"]
        
        # Подсчёт итогов
        total_score = sum(scores)
        if total_score == 0:
            percentages = {"code": 0, "data": 0, "design": 0, "security": 0}
        else:
            percentages = {
                "code": int((scores[0] / total_score) * 100),
                "data": int((scores[1] / total_score) * 100),
                "design": int((scores[2] / total_score) * 100),
                "security": int((scores[3] / total_score) * 100)
            }
        
        # Определяем специализацию
        max_index = scores.index(max(scores))
        specializations = ["Программная инженерия", "Data Science", "UX/UI дизайн", "Кибербезопасность"]
        result = f"""
🎉 <b>Тест завершен!</b>

📊 <b>Ваши результаты:</b>
• Программная инженерия: {percentages['code']}%
• Data Science: {percentages['data']}%
• UX/UI дизайн: {percentages['design']}%
• Кибербезопасность: {percentages['security']}%

🎯 <b>Рекомендуемая специализация:</b>
<b>{specializations[max_index]}</b>

Нажмите /start для нового теста
"""
        send_message(chat_id, result, get_main_menu())
        del user_sessions[user_id]
        return
    
    # Отправляем вопрос
    q = QUESTIONS[q_num - 1]
    text = f"❓ <b>Вопрос {q_num}/{len(QUESTIONS)}</b>\n\n{q['text']}"
    markup = get_question_keyboard(q["options"])
    send_message(chat_id, text, markup)

# Обработчик вебхука
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
        send_message(chat_id, "🎓 Добро пожаловать в IT-профориентатор!\n\nНажмите 'Начать тест'", get_main_menu())
        return jsonify({"ok": True})
    
    # Кнопка "Начать тест"
    if text == 'Начать тест':
        user_sessions[user_id] = {"current": 1, "scores": [0, 0, 0, 0]}
        send_question(chat_id, user_id, 1)
        return jsonify({"ok": True})
    
    # Кнопка "Помощь"
    if text == 'Помощь':
        send_message(chat_id, "Нажмите 'Начать тест' для прохождения теста\n\nВопросов: 5", get_main_menu())
        return jsonify({"ok": True})
    
    # Если пользователь в процессе теста
    if user_id in user_sessions:
        session = user_sessions[user_id]
        current = session["current"]
        
        if current <= len(QUESTIONS):
            q = QUESTIONS[current - 1]
            # Проверяем, что ответ правильный
            valid_answers = [opt["text"] for opt in q["options"]]
            if text in valid_answers:
                # Находим выбранный вариант и добавляем баллы
                for opt in q["options"]:
                    if opt["text"] == text:
                        # code, data, design, security
                        if text in ["Писать код", "Логически и последовательно", "Создавать новые продукты", "Индивидуально и глубоко", "Функциональность"]:
                            session["scores"][0] += opt["score"]
                        elif text in ["Анализировать данные", "Исследуя данные", "Понимать как работают системы", "Производительность"]:
                            session["scores"][1] += opt["score"]
                        elif text in ["Рисовать дизайн", "Интуитивно и творчески", "Делать интерфейсы красивыми", "Внешний вид"]:
                            session["scores"][2] += opt["score"]
                        else:
                            session["scores"][3] += opt["score"]
                        break
                session["current"] += 1
                send_question(chat_id, user_id, session["current"])
            else:
                send_message(chat_id, "❌ Пожалуйста, выберите вариант из кнопок")
        return jsonify({"ok": True})
    
    # Если ничего не подошло
    send_message(chat_id, "Нажмите 'Начать тест' для начала", get_main_menu())
    return jsonify({"ok": True})

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
