import json
import uuid
import threading
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import Base, UserAnswer, Specialization, University, UserSession, Question

class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False, "timeout": 30})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self._lock = threading.Lock()
    
    def _get_session(self):
        """Получить сессию с блокировкой"""
        return self.Session()
    
    def _close_session(self, session):
        """Безопасно закрыть сессию"""
        try:
            if session:
                session.close()
        except Exception as e:
            print(f"❌ Ошибка при закрытии сессии: {e}")
    
    def _retry_operation(self, operation, max_retries=3, delay=0.1):
        """Выполнить операцию с повторными попытками"""
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"🔄 Попытка {attempt + 1}/{max_retries}: БД заблокирована, ожидание...")
                    time.sleep(delay * (attempt + 1))
                    continue
                else:
                    raise e
    
    def get_question(self, question_id):
        """Получить вопрос по ID из БД"""
        def _get_question_operation():
            session = None
            try:
                with self._lock:
                    session = self._get_session()
                    question = session.query(Question).filter_by(id=question_id).first()
                    if question:
                        return {
                            "id": question.id,
                            "text": question.text,
                            "category": question.category,
                            "options": json.loads(question.options)
                        }
                    return None
            finally:
                self._close_session(session)
        
        try:
            return self._retry_operation(_get_question_operation)
        except Exception as e:
            print(f"❌ Ошибка в get_question: {e}")
            # Возвращаем вопрос из кода если БД недоступна
            return self._get_questions().get(question_id)
    
    def _get_questions(self):
        """Получить все вопросы теста"""
        return {
            1: {
                "id": 1,
                "text": "Как вы реагируете на новый гаджет/программу?",
                "category": "technical",
                "options": [
                    {"text": "Хочу разобрать/изучить его код", "value": 4, "category": "code"},
                    {"text": "Изучаю документацию и тех. характеристики", "value": 8, "category": "data"},
                    {"text": "Оцениваю дизайн и удобство интерфейса", "value": 12, "category": "design"},
                    {"text": "Проверяю настройки безопасности", "value": 16, "category": "security"}
                ]
            },
            2: {
                "id": 2,
                "text": "Ваш подход к решению технических проблем?",
                "category": "technical",
                "options": [
                    {"text": "Пишу алгоритм решения", "value": 4, "category": "code"},
                    {"text": "Собираю статистику ошибок", "value": 8, "category": "data"},
                    {"text": "Ищу красивое элегантное решение", "value": 12, "category": "design"},
                    {"text": "Анализирую возможные угрозы", "value": 16, "category": "security"}
                ]
            },
            3: {
                "id": 3,
                "text": "Какой проект вас больше увлечет?",
                "category": "technical",
                "options": [
                    {"text": "Оптимизация кода", "value": 4, "category": "code"},
                    {"text": "Прогнозирование трендов", "value": 8, "category": "data"},
                    {"text": "Создание логотипа", "value": 12, "category": "design"},
                    {"text": "Тестирование защиты системы", "value": 16, "category": "security"}
                ]
            },
            4: {
                "id": 4,
                "text": "Ваше отношение к математике?",
                "category": "technical",
                "options": [
                    {"text": "Нужна для алгоритмов", "value": 4, "category": "code"},
                    {"text": "Основа анализа данных", "value": 8, "category": "data"},
                    {"text": "Полезна для графики", "value": 12, "category": "design"},
                    {"text": "Важна для криптографии", "value": 16, "category": "security"}
                ]
            },
            5: {
                "id": 5,
                "text": "Какой язык вам интереснее?",
                "category": "technical",
                "options": [
                    {"text": "Python/Java", "value": 4, "category": "code"},
                    {"text": "SQL/R", "value": 8, "category": "data"},
                    {"text": "HTML/CSS", "value": 12, "category": "design"},
                    {"text": "Assembly", "value": 16, "category": "security"}
                ]
            },
            6: {
                "id": 6,
                "text": "Какой софт вам ближе?",
                "category": "technical",
                "options": [
                    {"text": "IDE (VSCode)", "value": 4, "category": "code"},
                    {"text": "Аналитические инструменты (Tableau)", "value": 8, "category": "data"},
                    {"text": "Графические редакторы (Figma)", "value": 12, "category": "design"},
                    {"text": "Сканеры уязвимостей", "value": 16, "category": "security"}
                ]
            },
            7: {
                "id": 7,
                "text": "Какой хобби-проект выберете?",
                "category": "technical",
                "options": [
                    {"text": "Сайт-портфолио", "value": 4, "category": "code"},
                    {"text": "Анализ своих привычек", "value": 8, "category": "data"},
                    {"text": "Дизайн постера", "value": 12, "category": "design"},
                    {"text": "Шифрование дневника", "value": 16, "category": "security"}
                ]
            },
            8: {
                "id": 8,
                "text": "Ваш стиль работы:",
                "category": "technical",
                "options": [
                    {"text": "Системный и структурированный", "value": 4, "category": "code"},
                    {"text": "Аналитический и точный", "value": 8, "category": "data"},
                    {"text": "Креативный и гибкий", "value": 12, "category": "design"},
                    {"text": "Осторожный и методичный", "value": 16, "category": "security"}
                ]
            },
            9: {
                "id": 9,
                "text": "Что важнее в проекте?",
                "category": "technical",
                "options": [
                    {"text": "Эффективность кода", "value": 4, "category": "code"},
                    {"text": "Достоверность данных", "value": 8, "category": "data"},
                    {"text": "Визуальная привлекательность", "value": 12, "category": "design"},
                    {"text": "Защищенность системы", "value": 16, "category": "security"}
                ]
            },
            10: {
                "id": 10,
                "text": "Какой курс выберете?",
                "category": "technical",
                "options": [
                    {"text": "Алгоритмы", "value": 4, "category": "code"},
                    {"text": "Машинное обучение", "value": 8, "category": "data"},
                    {"text": "Веб-дизайн", "value": 12, "category": "design"},
                    {"text": "Криптография", "value": 16, "category": "security"}
                ]
            },
            11: {
                "id": 11,
                "text": "Какой график работы вам подходит?",
                "category": "work_pref",
                "options": [
                    {"text": "Гибкий (удалёнка, свободные часы)", "value": 4, "category": "code"},
                    {"text": "Чёткий (с плановыми отчётами)", "value": 8, "category": "data"},
                    {"text": "Нестандартный (креативные спринты)", "value": 12, "category": "design"},
                    {"text": "Регламентированный (с соблюдением протоколов)", "value": 16, "category": "security"}
                ]
            },
            12: {
                "id": 12,
                "text": "Какой тип команды вам комфортен?",
                "category": "work_pref",
                "options": [
                    {"text": "Технические специалисты", "value": 4, "category": "code"},
                    {"text": "Аналитики и учёные", "value": 8, "category": "data"},
                    {"text": "Дизайнеры и копирайтеры", "value": 12, "category": "design"},
                    {"text": "Специалисты по compliance", "value": 16, "category": "security"}
                ]
            },
            13: {
                "id": 13,
                "text": "Какой проект вас вдохновит?",
                "category": "work_pref",
                "options": [
                    {"text": "Разработка движка для соцсети", "value": 4, "category": "code"},
                    {"text": "Прогнозирование биржевых трендов", "value": 8, "category": "data"},
                    {"text": "Создание айдентики бренда", "value": 12, "category": "design"},
                    {"text": "Аудит банковской системы", "value": 16, "category": "security"}
                ]
            },
            14: {
                "id": 14,
                "text": "Как вы относитесь к рутинным задачам?",
                "category": "work_pref",
                "options": [
                    {"text": "Автоматизирую", "value": 4, "category": "code"},
                    {"text": "Анализирую на улучшения", "value": 8, "category": "data"},
                    {"text": "Делаю их эстетичными", "value": 12, "category": "design"},
                    {"text": "Проверяю на риски", "value": 16, "category": "security"}
                ]
            },
            15: {
                "id": 15,
                "text": "Что для вас важно в работе?",
                "category": "work_pref",
                "options": [
                    {"text": "Сложные технические вызовы", "value": 4, "category": "code"},
                    {"text": "Точность и достоверность", "value": 8, "category": "data"},
                    {"text": "Визуальная гармония", "value": 12, "category": "design"},
                    {"text": "Надёжность и защищённость", "value": 16, "category": "security"}
                ]
            },
            16: {
                "id": 16,
                "text": "Какой формат обучения предпочитаете?",
                "category": "work_pref",
                "options": [
                    {"text": "Хакатоны и практика", "value": 4, "category": "code"},
                    {"text": "Исследования и статистика", "value": 8, "category": "data"},
                    {"text": "Воркшопы по креативу", "value": 12, "category": "design"},
                    {"text": "Кейсы по кибербезопасности", "value": 16, "category": "security"}
                ]
            },
            17: {
                "id": 17,
                "text": "Какой офис вам подойдёт?",
                "category": "work_pref",
                "options": [
                    {"text": "Коворкинг с IT-стартапами", "value": 4, "category": "code"},
                    {"text": "Лаборатория данных", "value": 8, "category": "data"},
                    {"text": "Студия с арт-пространством", "value": 12, "category": "design"},
                    {"text": "Офис с защищённой инфраструктурой", "value": 16, "category": "security"}
                ]
            },
            18: {
                "id": 18,
                "text": "Как вы принимаете решения?",
                "category": "work_pref",
                "options": [
                    {"text": "На основе логики", "value": 4, "category": "code"},
                    {"text": "На основе данных", "value": 8, "category": "data"},
                    {"text": "Интуитивно-образно", "value": 12, "category": "design"},
                    {"text": "Через оценку рисков", "value": 16, "category": "security"}
                ]
            },
            19: {
                "id": 19,
                "text": "Какой журнал вы купите?",
                "category": "work_pref",
                "options": [
                    {"text": "Хакер", "value": 4, "category": "code"},
                    {"text": "Harvard Business Review", "value": 8, "category": "data"},
                    {"text": "Как (о дизайне)", "value": 12, "category": "design"},
                    {"text": "Information Security", "value": 16, "category": "security"}
                ]
            },
            20: {
                "id": 20,
                "text": "Ваш подход к ошибкам?",
                "category": "work_pref",
                "options": [
                    {"text": "Разбираю баги", "value": 4, "category": "code"},
                    {"text": "Ищу закономерности", "value": 8, "category": "data"},
                    {"text": "Превращаю в фичу", "value": 12, "category": "design"},
                    {"text": "Устраняю уязвимости", "value": 16, "category": "security"}
                ]
            },
            21: {
                "id": 21,
                "text": "Как вас описывают друзья?",
                "category": "personal",
                "options": [
                    {"text": "Технарь", "value": 4, "category": "code"},
                    {"text": "Аналитик", "value": 8, "category": "data"},
                    {"text": "Творческий", "value": 12, "category": "design"},
                    {"text": "Бдительный", "value": 16, "category": "security"}
                ]
            },
            22: {
                "id": 22,
                "text": "Ваша суперсила?",
                "category": "personal",
                "options": [
                    {"text": "Решение сложных задач", "value": 4, "category": "code"},
                    {"text": "Нахождение закономерностей", "value": 8, "category": "data"},
                    {"text": "Генерирование идей", "value": 12, "category": "design"},
                    {"text": "Предвидение рисков", "value": 16, "category": "security"}
                ]
            },
            23: {
                "id": 23,
                "text": "Какой фильм вам ближе?",
                "category": "personal",
                "options": [
                    {"text": "Социальная сеть", "value": 4, "category": "code"},
                    {"text": "Игра на понижение", "value": 8, "category": "data"},
                    {"text": "Отель Гранд Будапешт", "value": 12, "category": "design"},
                    {"text": "Война миров Z", "value": 16, "category": "security"}
                ]
            },
            24: {
                "id": 24,
                "text": "Ваш стиль мышления?",
                "category": "personal",
                "options": [
                    {"text": "Алгоритмический", "value": 4, "category": "code"},
                    {"text": "Системный", "value": 8, "category": "data"},
                    {"text": "Ассоциативный", "value": 12, "category": "design"},
                    {"text": "Осторожный", "value": 16, "category": "security"}
                ]
            },
            25: {
                "id": 25,
                "text": "Что вас раздражает?",
                "category": "personal",
                "options": [
                    {"text": "Неоптимальный код", "value": 4, "category": "code"},
                    {"text": "Неточные данные", "value": 8, "category": "data"},
                    {"text": "Безвкусица", "value": 12, "category": "design"},
                    {"text": "Беспечность", "value": 16, "category": "security"}
                ]
            },
            26: {
                "id": 26,
                "text": "Как отдыхаете?",
                "category": "personal",
                "options": [
                    {"text": "Участвую в CTF-соревнованиях", "value": 4, "category": "code"},
                    {"text": "Анализирую свои привычки", "value": 8, "category": "data"},
                    {"text": "Посещаю выставки", "value": 12, "category": "design"},
                    {"text": "Изучаю схемы защиты", "value": 16, "category": "security"}
                ]
            },
            27: {
                "id": 27,
                "text": "Ваш девиз?",
                "category": "personal",
                "options": [
                    {"text": "Move fast and break things", "value": 4, "category": "code"},
                    {"text": "Data never lies", "value": 8, "category": "data"},
                    {"text": "Design is intelligence made visible", "value": 12, "category": "design"},
                    {"text": "Security first", "value": 16, "category": "security"}
                ]
            },
            28: {
                "id": 28,
                "text": "Какой гаджет купите?",
                "category": "personal",
                "options": [
                    {"text": "Raspberry Pi", "value": 4, "category": "code"},
                    {"text": "Графический планшет", "value": 8, "category": "data"},
                    {"text": "Wacom Cintiq", "value": 12, "category": "design"},
                    {"text": "YubiKey", "value": 16, "category": "security"}
                ]
            },
            29: {
                "id": 29,
                "text": "Как учитесь новому?",
                "category": "personal",
                "options": [
                    {"text": "Через практику", "value": 4, "category": "code"},
                    {"text": "Через исследования", "value": 8, "category": "data"},
                    {"text": "Через вдохновение", "value": 12, "category": "design"},
                    {"text": "Через стандарты", "value": 16, "category": "security"}
                ]
            },
            30: {
                "id": 30,
                "text": "Ваша цель в IT?",
                "category": "personal",
                "options": [
                    {"text": "Создать технологичный продукт", "value": 4, "category": "code"},
                    {"text": "Найти инсайты в данных", "value": 8, "category": "data"},
                    {"text": "Делать цифровую среду красивее", "value": 12, "category": "design"},
                    {"text": "Защитить информацию", "value": 16, "category": "security"}
                ]
            }
        }
    
    def create_user_session(self, user_id):
        """Создать новую сессию пользователя"""
        def _create_session_operation():
            session = None
            try:
                with self._lock:
                    session = self._get_session()
                    session_id = str(uuid.uuid4())
                    user_session = UserSession(
                        user_id=user_id,
                        session_id=session_id,
                        current_question=1,
                        answers="{}",
                        is_completed=0
                    )
                    session.add(user_session)
                    session.commit()
                    return session_id
            finally:
                self._close_session(session)
        
        try:
            return self._retry_operation(_create_session_operation)
        except Exception as e:
            print(f"❌ Ошибка в create_user_session: {e}")
            # Возвращаем простой session_id если БД недоступна
            return str(uuid.uuid4())
    
    def get_user_session(self, user_id):
        """Получить активную сессию пользователя"""
        def _get_session_operation():
            session = None
            try:
                with self._lock:
                    session = self._get_session()
                    user_session = session.query(UserSession).filter_by(
                        user_id=user_id, 
                        is_completed=0
                    ).first()
                    return user_session
            finally:
                self._close_session(session)
        
        try:
            return self._retry_operation(_get_session_operation)
        except Exception as e:
            print(f"❌ Ошибка в get_user_session: {e}")
            return None
    
    def update_user_answers(self, user_id, question_id, answer_value):
        """Обновить ответы пользователя"""
        def _update_answers_operation():
            session = None
            try:
                with self._lock:
                    session = self._get_session()
                    user_session = session.query(UserSession).filter_by(
                        user_id=user_id, 
                        is_completed=0
                    ).first()
                    
                    if user_session:
                        answers = json.loads(user_session.answers)
                        answers[str(question_id)] = answer_value
                        user_session.answers = json.dumps(answers)
                        user_session.current_question = question_id + 1
                        
                        if question_id >= 30:
                            user_session.is_completed = 1
                        
                        session.commit()
            finally:
                self._close_session(session)
        
        try:
            self._retry_operation(_update_answers_operation)
        except Exception as e:
            print(f"❌ Ошибка в update_user_answers: {e}")
    
    def get_specialization_from_code(self, spec_name):
        """Получить информацию о специализации из кода (fallback)"""
        specializations = {
            "Программная инженерия": {
                "id": 1,
                "name": "Программная инженерия",
                "description": "Разработка и сопровождение программного обеспечения. Создание эффективных алгоритмов, архитектуры систем и оптимизация производительности.",
                "skills": "• Программирование (Python, Java, C++)\n• Алгоритмы и структуры данных\n• Архитектура ПО\n• DevOps практики\n• Работа с базами данных",
                "careers": "• Backend-разработчик\n• DevOps-инженер\n• Архитектор ПО\n• Team Lead"
            },
            "Data Science": {
                "id": 2,
                "name": "Data Science",
                "description": "Анализ больших данных, машинное обучение и извлечение инсайтов для принятия бизнес-решений.",
                "skills": "• Статистика и математика\n• Машинное обучение\n• Python/R/SQL\n• Визуализация данных\n• Big Data технологии",
                "careers": "• Специалист по обработке данных\n• Аналитик данных\n• ML-инженер\n• Специалист по бизнес-аналитике"
            },
            "UX/UI дизайн": {
                "id": 3,
                "name": "UX/UI дизайн",
                "description": "Создание удобных и красивых пользовательских интерфейсов. Исследование пользовательского опыта и проектирование взаимодействий.",
                "skills": "• Figma, Sketch, Adobe XD\n• Принципы UX/UI\n• Прототипирование\n• Аналитика поведения\n• Типографика и цветоведение",
                "careers": "• UX-дизайнер\n• UI-дизайнер\n• Продуктовый дизайнер\n• UX-исследователь"
            },
            "Кибербезопасность": {
                "id": 4,
                "name": "Кибербезопасность",
                "description": "Защита информационных систем от киберугроз. Анализ уязвимостей и разработка защитных механизмов.",
                "skills": "• Сетевые протоколы\n• Криптография\n• Penetration Testing\n• Forensics\n• Compliance и аудит",
                "careers": "• Инженер по безопасности\n• Пентестер\n• Аналитик безопасности\n• CISO"
            },
            "DevOps инженерия": {
                "id": 5,
                "name": "DevOps инженерия",
                "description": "Автоматизация процессов разработки и развертывания. Управление инфраструктурой и обеспечение непрерывной интеграции.",
                "skills": "• Docker, Kubernetes\n• CI/CD (Jenkins, GitLab)\n• Облачные платформы (AWS, Azure)\n• Мониторинг и логирование\n• Linux и скриптинг",
                "careers": "• DevOps-инженер\n• SRE-инженер\n• Облачный инженер\n• Платформенный инженер"
            },
            "Мобильная разработка": {
                "id": 6,
                "name": "Мобильная разработка",
                "description": "Создание приложений для iOS и Android. Разработка нативных и кроссплатформенных решений.",
                "skills": "• Swift/Objective-C (iOS)\n• Kotlin/Java (Android)\n• React Native/Flutter\n• UI/UX для мобильных\n• App Store оптимизация",
                "careers": "• iOS-разработчик\n• Android-разработчик\n• Мобильный разработчик\n• React Native-разработчик"
            },
            "Game Development": {
                "id": 7,
                "name": "Game Development",
                "description": "Разработка игр для различных платформ. Создание игровых механик, графики и пользовательского опыта.",
                "skills": "• Unity/Unreal Engine\n• C#/C++\n• 3D моделирование\n• Игровая физика\n• Звуковой дизайн",
                "careers": "• Игровой разработчик\n• Unity-разработчик\n• Гейм-дизайнер\n• Технический художник"
            },
            "AI/ML инженерия": {
                "id": 8,
                "name": "AI/ML инженерия",
                "description": "Разработка систем искусственного интеллекта и машинного обучения. Создание алгоритмов для решения сложных задач.",
                "skills": "• Deep Learning (PyTorch, TensorFlow)\n• Computer Vision\n• NLP\n• MLOps\n• Математическая оптимизация",
                "careers": "• ML-инженер\n• Исследователь ИИ\n• Инженер компьютерного зрения\n• NLP-инженер"
            }
        }
        return specializations.get(spec_name, None)
    
    # Админ-методы для управления
    def get_all_universities(self):
        """Получить все вузы"""
        # Получаем все вузы из кода (так как они хранятся в коде)
        all_universities = []
        
        # Собираем все вузы из всех специализаций
        specializations = [
            "Программная инженерия", "Data Science", "UX/UI дизайн", "Кибербезопасность",
            "DevOps инженерия", "Мобильная разработка", "Game Development", "AI/ML инженерия"
        ]
        
        uni_id = 1
        for spec_name in specializations:
            spec_universities = self.get_universities(spec_name)
            if spec_universities:
                for uni in spec_universities:
                    all_universities.append({
                        'id': uni_id,
                        'name': uni['name'],
                        'specialization_id': self.get_specialization_id_by_name(spec_name),
                        'score_min': uni['score_min'],
                        'score_max': uni['score_max'],
                        'location': uni['location'],
                        'url': uni['url']
                    })
                    uni_id += 1
        
        return all_universities
    
    def add_university(self, name, specialization_id, score_min, score_max, location, url):
        """Добавить новый вуз"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                university = University(
                    name=name,
                    specialization_id=specialization_id,
                    score_min=score_min,
                    score_max=score_max,
                    location=location,
                    url=url
                )
                session.add(university)
                session.commit()
                return university.id
        finally:
            self._close_session(session)
    
    def delete_university(self, university_id):
        """Удалить вуз по ID"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                university = session.query(University).filter_by(id=university_id).first()
                if university:
                    session.delete(university)
                    session.commit()
                    return True
                return False
        finally:
            self._close_session(session)
    
    def get_all_questions(self):
        """Получить все вопросы из БД"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                questions = session.query(Question).all()
                result = {}
                for q in questions:
                    result[q.id] = {
                        "id": q.id,
                        "text": q.text,
                        "category": q.category,
                        "options": json.loads(q.options)
                    }
                return result
        finally:
            self._close_session(session)
    
    def add_question(self, question_data):
        """Добавить новый вопрос в БД"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                question = Question(
                    text=question_data['text'],
                    options=json.dumps(question_data['options']),
                    category=question_data['category']
                )
                session.add(question)
                session.commit()
                return question.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self._close_session(session)
    
    def delete_question(self, question_id):
        """Удалить вопрос из БД"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                question = session.query(Question).filter_by(id=question_id).first()
                if question:
                    session.delete(question)
                    session.commit()
                    return True
                return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self._close_session(session)
    
    def get_user_statistics(self):
        """Получить статистику пользователей"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                total_users = session.query(UserSession.user_id).distinct().count()
                active_sessions = session.query(UserSession).filter_by(is_completed=0).count()
                completed_tests = session.query(UserSession).filter_by(is_completed=1).count()
                
                return {
                    'total_users': total_users,
                    'active_sessions': active_sessions,
                    'completed_tests': completed_tests
                }
        finally:
            self._close_session(session)
    
    def get_specialization_id_by_name(self, spec_name):
        """Получить ID специализации по названию из БД"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                spec = session.query(Specialization).filter_by(name=spec_name).first()
                return spec.id if spec else None
        finally:
            self._close_session(session)
    
    def get_all_users(self):
        """Получить всех пользователей для рассылки"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                users = session.query(UserSession.user_id).distinct().all()
                return [user[0] for user in users]
        finally:
            self._close_session(session)
    
    def get_university(self, university_id):
        """Получить вуз по ID"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                university = session.query(University).filter_by(id=university_id).first()
                if university:
                    return {
                        'id': university.id,
                        'name': university.name,
                        'specialization_id': university.specialization_id,
                        'score_min': university.score_min,
                        'score_max': university.score_max,
                        'location': university.location,
                        'url': university.url
                    }
                return None
        finally:
            self._close_session(session)
    
    def get_all_specializations(self):
        """Получить все специализации из БД"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                specs = session.query(Specialization).all()
                result = {}
                for spec in specs:
                    result[spec.id] = {
                        "id": spec.id,
                        "name": spec.name,
                        "description": spec.description,
                        "tech_score": spec.tech_score,
                        "analytic_score": spec.analytic_score,
                        "creative_score": spec.creative_score,
                        "careers": spec.careers
                    }
                return result
        finally:
            self._close_session(session)
    
    def get_specialization(self, spec_name):
        """Получить специализацию по названию из БД с fallback"""
        def _get_specialization_operation():
            session = None
            try:
                with self._lock:
                    session = self._get_session()
                    spec = session.query(Specialization).filter_by(name=spec_name).first()
                    if spec:
                        return {
                            "id": spec.id,
                            "name": spec.name,
                            "description": spec.description,
                            "tech_score": spec.tech_score,
                            "analytic_score": spec.analytic_score,
                            "creative_score": spec.creative_score,
                            "careers": spec.careers
                        }
                    return None
            finally:
                self._close_session(session)
        
        try:
            result = self._retry_operation(_get_specialization_operation)
            if result:
                return result
            else:
                # Fallback к данным из кода
                return self.get_specialization_from_code(spec_name)
        except Exception as e:
            print(f"❌ Ошибка в get_specialization: {e}")
            # Fallback к данным из кода
            return self.get_specialization_from_code(spec_name)
    
    def get_universities(self, spec_name):
        """Получить список вузов для специализации из БД"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                # Получаем специализацию
                spec = session.query(Specialization).filter_by(name=spec_name).first()
                if not spec:
                    return []
                
                # Получаем университеты для этой специализации
                universities = session.query(University).filter_by(specialization_id=spec.id).all()
                
                # Преобразуем в нужный формат
                result = []
                for uni in universities:
                    result.append({
                        "name": uni.name,
                        "score_min": uni.score_min,
                        "score_max": uni.score_max,
                        "url": uni.url,
                        "location": uni.location,
                        "program": f"Специализация: {spec_name}"
                    })
                
                return result
        finally:
            self._close_session(session)
    def get_universities_by_specialization(self, specialization_id):
        """Получить университеты по ID специализации из БД"""
        def _get_universities_operation():
            session = None
            try:
                with self._lock:
                    session = self._get_session()
                    universities = session.query(University).filter_by(specialization_id=specialization_id).all()
                    
                    result = []
                    for uni in universities:
                        result.append({
                            "id": uni.id,
                            "name": uni.name,
                            "city": uni.location.split(',')[0] if uni.location else "Неизвестный город",
                            "score_min": uni.score_min,
                            "score_max": uni.score_max,
                            "url": uni.url,
                            "location": uni.location
                        })
                    
                    return result
            finally:
                self._close_session(session)
        
        try:
            return self._retry_operation(_get_universities_operation)
        except Exception as e:
            print(f"❌ Ошибка в get_universities_by_specialization: {e}")
            # Возвращаем тестовые данные если БД недоступна
            return [
                {"id": 1, "name": "МГУ им. М.В. Ломоносова", "city": "Москва", "score_min": 85, "score_max": 100, "url": "https://www.msu.ru", "location": "Москва"},
                {"id": 2, "name": "СПбГУ", "city": "Санкт-Петербург", "score_min": 80, "score_max": 95, "url": "https://spbu.ru", "location": "Санкт-Петербург"},
                {"id": 3, "name": "МФТИ", "city": "Москва", "score_min": 90, "score_max": 100, "url": "https://mipt.ru", "location": "Москва"},
                {"id": 4, "name": "ИТМО", "city": "Санкт-Петербург", "score_min": 85, "score_max": 98, "url": "https://itmo.ru", "location": "Санкт-Петербург"}
            ]
    
    def add_specialization(self, name, description, tech_score, analytic_score, creative_score, careers):
        """Добавить новую специализацию"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                specialization = Specialization(
                    name=name,
                    description=description,
                    tech_score=tech_score,
                    analytic_score=analytic_score,
                    creative_score=creative_score,
                    careers=careers
                )
                session.add(specialization)
                session.commit()
                return specialization.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self._close_session(session)
    
    def delete_specialization(self, specialization_id):
        """Удалить специализацию по ID"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                specialization = session.query(Specialization).filter_by(id=specialization_id).first()
                if specialization:
                    session.delete(specialization)
                    session.commit()
                    return True
                return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            self._close_session(session)
    
    def get_specialization_by_id(self, specialization_id):
        """Получить специализацию по ID"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                spec = session.query(Specialization).filter_by(id=specialization_id).first()
                if spec:
                    return {
                        "id": spec.id,
                        "name": spec.name,
                        "description": spec.description,
                        "tech_score": spec.tech_score,
                        "analytic_score": spec.analytic_score,
                        "creative_score": spec.creative_score,
                        "careers": spec.careers
                    }
                return None
        finally:
            self._close_session(session)
 
    def get_unique_universities_count(self):
        """Количество уникальных вузов по имени"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                result = session.execute(text("SELECT COUNT(DISTINCT name) FROM universities")).scalar()
                return int(result or 0)
        finally:
            self._close_session(session)

    def get_unique_universities(self):
        """Список уникальных вузов: name, location, url (по первому вхождению)"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                rows = session.execute(text(
                    """
                    SELECT name,
                           MIN(location) AS location,
                           MIN(COALESCE(url, '')) AS url
                    FROM universities
                    GROUP BY name
                    ORDER BY name COLLATE NOCASE
                    """
                )).all()
                return [{"name": r[0], "location": r[1], "url": (r[2] or None)} for r in rows]
        finally:
            self._close_session(session)

    def delete_university_by_name(self, uni_name):
        """Удалить все записи вуза по имени"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                session.execute(text("DELETE FROM universities WHERE name = :n"), {"n": uni_name})
                session.commit()
                return True
        except Exception as e:
            if session:
                session.rollback()
            raise e
        finally:
            self._close_session(session)

    def get_specialization_names(self):
        """Вернуть список названий специализаций из БД"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                rows = session.execute(text("SELECT name FROM specializations ORDER BY name COLLATE NOCASE")).all()
                return [r[0] for r in rows]
        finally:
            self._close_session(session)

    def export_universities_to_json(self, out_path):
        """Экспортировать все записи вузов в JSON (для сайта)"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                rows = session.execute(text(
                    """
                    SELECT u.name, u.location, u.score_min, u.score_max, u.url, s.name AS specialization
                    FROM universities u
                    LEFT JOIN specializations s ON s.id = u.specialization_id
                    ORDER BY u.name COLLATE NOCASE
                    """
                )).all()
                data = []
                for name, location, smin, smax, url, spec in rows:
                    data.append({
                        "name": name,
                        "city": location,
                        "score_min": smin,
                        "score_max": smax,
                        "url": url,
                        "specialization": spec,
                    })
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return len(data)
        finally:
            self._close_session(session)

    def sync_website_data(self):
        """Синхронизировать данные с сайтом - экспорт в JSON и обновление HTML"""
        try:
            # Экспортируем данные в JSON
            count = self.export_universities_to_json('universities.json')
            print(f"✅ Экспортировано {count} записей вузов в universities.json")
            
            # Обновляем HTML файл с встроенными данными
            self.update_universities_html()
            
            return True
        except Exception as e:
            print(f"❌ Ошибка синхронизации сайта: {e}")
            return False

    def update_universities_html(self):
        """Обновить universities.html с актуальными данными"""
        try:
            # Получаем данные вузов
            session = None
            try:
                with self._lock:
                    session = self._get_session()
                    rows = session.execute(text(
                        """
                        SELECT u.name, u.location, u.score_min, u.score_max, u.url, s.name AS specialization
                        FROM universities u
                        LEFT JOIN specializations s ON s.id = u.specialization_id
                        ORDER BY u.name COLLATE NOCASE
                        """
                    )).all()
                    universities_data = []
                    for name, location, smin, smax, url, spec in rows:
                        universities_data.append({
                            "name": name,
                            "city": location,
                            "score_min": smin,
                            "score_max": smax,
                            "url": url,
                            "specialization": spec,
                        })
            finally:
                self._close_session(session)
            
            # Читаем текущий HTML файл
            try:
                with open('universities.html', 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except FileNotFoundError:
                print("❌ Файл universities.html не найден")
                return
            
            # Находим и заменяем данные в HTML
            import re
            
            # Конвертируем данные в JSON для вставки в HTML
            universities_json = json.dumps(universities_data, ensure_ascii=False, indent=2)
            
            # Заменяем данные в HTML
            pattern = r'window\.EMBEDDED_UNIVERSITIES = \[.*?\];'
            replacement = f'window.EMBEDDED_UNIVERSITIES = {universities_json};'
            
            new_html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
            
            # Обновляем счетчики в HTML
            # Подсчитываем уникальные вузы
            unique_universities = set()
            for uni in universities_data:
                unique_universities.add(uni['name'])
            
            # Заменяем счетчик уникальных вузов
            uni_count_pattern = r'<strong id="uniqueUniCount">\d+</strong>'
            uni_count_replacement = f'<strong id="uniqueUniCount">{len(unique_universities)}</strong>'
            new_html_content = re.sub(uni_count_pattern, uni_count_replacement, new_html_content)
            
            # Заменяем счетчик общих специализаций
            specs_count_pattern = r'<strong id="totalSpecsCount">\d+</strong>'
            specs_count_replacement = f'<strong id="totalSpecsCount">{len(universities_data)}</strong>'
            new_html_content = re.sub(specs_count_pattern, specs_count_replacement, new_html_content)
            
            # Записываем обновленный HTML
            with open('universities.html', 'w', encoding='utf-8') as f:
                f.write(new_html_content)
            
            print(f"✅ Обновлен universities.html с {len(universities_data)} вузами")
            
        except Exception as e:
            print(f"❌ Ошибка обновления HTML: {e}")

    def get_university_id_by_name(self, uni_name):
        """Получить ID вуза по названию (первое вхождение)"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                result = session.execute(text("SELECT id FROM universities WHERE name = :n ORDER BY id LIMIT 1"), {"n": uni_name}).scalar()
                return int(result) if result else None
        finally:
            self._close_session(session)

    def get_university_name_by_id(self, uni_id):
        """Получить название вуза по ID"""
        session = None
        try:
            with self._lock:
                session = self._get_session()
                result = session.execute(text("SELECT name FROM universities WHERE id = :id"), {"id": uni_id}).scalar()
                return result
        finally:
            self._close_session(session)
 