💡 Статус проекта

Чек-лист готовности:

Backend API: Основные эндпоинты для управления пользователями и событиями реализованы.

База данных: Схема спроектирована и готова к работе.

Frontend: Реализованы только базовые компоненты, требуется дальнейшая разработка интерфейса и бизнес-логики.



Скриншоты интерфейса

![image](https://github.com/user-attachments/assets/2aab32d9-561e-43b4-bc14-ce437de5bcb0)

Архитектура проекта

разделение на Frontend и Backend.

Backend (Flask API)

Бэкенд представляет собой REST API, построенный на Flask. Его архитектура реализует принципы, схожие с Model-View-Controller (MVC):

Model (Модель): Определена в app/models.py с использованием Flask-SQLAlchemy. Этот слой отвечает за структуру данных, связи между таблицами и всю логику взаимодействия с базой данных PostgreSQL.

View (Представление): В контексте REST API, "представлением" является JSON-ответ. Функции в routes.py, использующие jsonify(), формируют это представление данных для клиента.

Controller (Контроллер): Роль контроллера выполняют функции-обработчики маршрутов в app/routes.py. Они принимают HTTP-запросы от клиента, обращаются к Модели для получения или изменения данных и возвращают результат в виде JSON-представления.

Frontend (React SPA)

Фронтенд — это Single Page Application (SPA), созданное с помощью React и Vite. Он следует компонентной архитектуре:

Components: UI разбит на небольшие, переиспользуемые компоненты (components/).

Pages: Компоненты-страницы, которые собираются из более мелких компонентов (pages/).

Services: Логика взаимодействия с API вынесена в отдельный слой (services/) для чистоты кода.

Context: Глобальное состояние (например, аутентификация пользователя) управляется с помощью React Context (context/).

Routing: Навигация по приложению без перезагрузки страницы реализована с помощью react-router-dom.

Технологический стек
Backend

Framework: Flask

ORM: Flask-SQLAlchemy

Аутентификация: Flask-JWT-Extended (JSON Web Tokens)

Frontend

Библиотека: React

Сборщик: Vite

Роутинг: React Router DOM

Формы: Formik (управление состоянием) и Yup (валидация)

База данных

PostgreSQL

Запуск проекта для разработки
Предварительные требования

Установленный Python 3.8+

Установленный Node.js 16+

Установленный и запущенный сервер PostgreSQL

1. Настройка Backend
Generated bash
# 1. Перейдите в папку бэкенда
cd backend

# 2. Создайте и активируйте виртуальное окружение (для Windows)
python -m venv venv
venv\Scripts\activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Настройте подключение к базе данных
# Скопируйте файл .env.example в .env и укажите в нем ваши данные для подключения к PostgreSQL
# Пример .env:
# DATABASE_URL="postgresql://user:password@localhost:5432/hr_portal_db"
# JWT_SECRET_KEY="ваш_супер_секретный_ключ"

# 5. Создайте таблицы в базе данных
# Выполните SQL-скрипт из файла schema.sql в вашем PostgreSQL клиенте (например, pgAdmin).

# 6. Запустите Flask-сервер
flask run


Бэкенд будет доступен по адресу http://localhost:5000.

2. Настройка Frontend
Generated bash
# 1. Откройте новый терминал и перейдите в папку фронтенда
cd frontend

# 2. Установите зависимости
npm install

# 3. Запустите сервер для разработки
npm run dev
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Фронтенд будет доступен по адресу http://localhost:5173. Откройте эту ссылку в браузере.

<details>
<summary><strong>Краткая сводка по API эндпоинтам</strong></summary>


POST /api/login - Вход в систему

GET, POST /api/users - Управление пользователями (только админ)

GET, PUT, DELETE /api/users/<id> - Управление конкретным пользователем (только админ)

GET /api/profile - Получение своего профиля

POST, GET /api/events - Создание и получение событий (отпусков, больничных)

PUT /api/events/<id>/status - Утверждение/отклонение заявок (только админ)

DELETE /api/events/<id> - Отмена заявки

GET /api/calendar/events - Получение данных для общего календаря

</details>
