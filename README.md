
💡 **Статус проекта**

**Чек-лист готовности:**
- **Backend API:** основные эндпоинты для управления пользователями и событиями реализованы  
- **База данных:** схема спроектирована и готова к работе  
- **Frontend:** реализованы только базовые компоненты, требуется дальнейшая разработка интерфейса и бизнес-логики  

## Скриншоты интерфейса

![Главный экран](https://github.com/user-attachments/assets/2aab32d9-561e-43b4-bc14-ce437de5bcb0)

## Архитектура проекта

Проект разделён на два модуля: Frontend и Backend.

### Backend (Flask API)

- **Model (Модель):** `app/models.py` (Flask-SQLAlchemy) — структура данных и взаимодействие с PostgreSQL  
- **View (Представление):** JSON-ответы через `jsonify()` в `routes.py`  
- **Controller (Контроллер):** обработчики маршрутов в `app/routes.py`

### Frontend (React SPA)

- **Components:** переиспользуемые UI-компоненты (`src/components/`)  
- **Pages:** страницы, собранные из компонентов (`src/pages/`)  
- **Services:** слой взаимодействия с API (`src/services/`)  
- **Context:** глобальное состояние (React Context) (`src/context/`)  
- **Routing:** навигация без перезагрузки (react-router-dom)

## Технологический стек

**Backend:** Flask, Flask-SQLAlchemy, Flask-JWT-Extended  
**Frontend:** React, Vite, React Router DOM, Formik, Yup  
**База данных:** PostgreSQL

## Запуск проекта для разработки

### Предварительные требования

- Python ≥ 3.8  
- Node.js ≥ 16  
- Запущенный сервер PostgreSQL

### 1. Настройка Backend

```bash
# Перейдите в папку backend
cd backend

# Создайте и активируйте виртуальное окружение (Windows)
python -m venv venv
venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt

# Скопируйте .env.example в .env и укажите параметры подключения
# Пример .env:
# DATABASE_URL="postgresql://user:password@localhost:5432/your_db"
# JWT_SECRET_KEY="ваш_секретный_ключ"

# Создайте таблицы в базе данных (schema.sql)
# Запустите Flask-сервер
flask run

Бэкенд будет доступен по адресу http://localhost:5000.

2. Настройка Frontend
Generated bash
# Перейдите в папку frontend
cd frontend

# Установите зависимости
npm install

# Запустите сервер разработки
npm run dev