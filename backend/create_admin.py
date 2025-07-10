import requests
import json

API_BASE_URL = "http://localhost:5000/api"

new_admin_payload = {
    "full_name": "Администратор Системы",
    "email": "admin2@company.com",
    "password": "228228",  # Используйте надежный пароль
    "role": "admin"  # Ключевое поле для создания админа
}


def create_admin_user():
    """Отправляет POST-запрос для создания нового пользователя-администратора."""

    create_user_url = f"{API_BASE_URL}/users"

    print(f"Отправка запроса на: {create_user_url}")
    print("Данные для отправки:")
    print(json.dumps(new_admin_payload, indent=4, ensure_ascii=False))

    try:
        response = requests.post(create_user_url, json=new_admin_payload)

        if response.status_code == 201:  # 201 Created - стандартный ответ при успешном создании
            print("\n✅ УСПЕХ! Пользователь-администратор успешно создан.")
            print("Ответ сервера:")
            print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        else:
            print(f"\n❌ ОШИБКА! Сервер ответил с кодом: {response.status_code}")
            try:
                print("Сообщение от сервера:", response.json())
            except json.JSONDecodeError:
                print("Не удалось прочитать ответ сервера в формате JSON. Текст ответа:", response.text)

    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ! Не удалось подключиться к серверу.")
        print("Убедитесь, что ваш Flask-сервер запущен на http://localhost:5000")
    except Exception as e:
        print(f"\nПроизошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    create_admin_user()