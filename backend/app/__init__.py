import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

# Загружаем переменные окружения из .env файла
load_dotenv()

# Инициализируем расширения (но пока не привязываем к приложению)
db = SQLAlchemy()

def create_app():
    """Фабрика для создания экземпляра приложения Flask."""
    app = Flask(__name__)

    # Конфигурация
    app.config['SECRET_KEY'] = 'a_very_secret_key_for_sessions' # Замените на случайную строку
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config["JWT_SECRET_KEY"] = "your-super-secret-jwt-key"  # <-- CHANGE THIS and put it in .env
    jwt = JWTManager(app)

    # Настройка CORS
    # Разрешаем запросы от нашего frontend-сервера разработки (Vite по умолчанию работает на порту 5173)
    # к любым маршрутам, начинающимся с /api/
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    # Инициализация расширений в контексте приложения
    db.init_app(app)

    # Регистрация маршрутов (Blueprints)
    from . import routes
    app.register_blueprint(routes.bp)

    return app