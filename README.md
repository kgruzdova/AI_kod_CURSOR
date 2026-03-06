# CURSOR — API и утилиты для пользователей

Flask-приложение для управления пользователями с SQLite, потокобезопасными операциями и безопасной работой с паролями.

## Структура проекта

```
CURSOR/
├── api.py          # Flask API с REST-эндпоинтами
├── utils.py        # Утилиты (БД, кэш, пароли)
├── requirements.txt
└── README.md
```

## Установка

### Требования

- Python 3.10+

### Шаги

```bash
# Создание виртуального окружения (рекомендуется)
python -m venv venv

# Активация
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

## Запуск API

```bash
python api.py
```

Сервер будет доступен по адресу `http://0.0.0.0:8080`.

## Docker

```bash
# Сборка и запуск
docker build -t cursor-api .
docker run -p 8080:8080 cursor-api

# Запуск на сервере (в фоне)
docker run -d -p 8080:8080 --name cursor-api cursor-api
```

**Публикация в Docker Hub и развёртывание на сервере** — см. [DEPLOY.md](DEPLOY.md).

## Проверка эндпоинтов

```bash
python check_endpoints.py
# или с другим URL:
python check_endpoints.py http://localhost:8080
```

Скрипт проверяет все 7 сценариев: POST /adduser, GET /user/1, 404, /activate, /slow, /wrong, валидация 400.

## API

### Пользователи

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/adduser` | Добавить пользователя |
| GET | `/user/<uid>` | Получить пользователя по ID |

### Дополнительные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/activate/<uid>` | Добавить uid в список активных (асинхронно) |
| GET | `/slow` | Тяжёлые вычисления (блокирует запрос) |
| GET | `/wrong` | Пример обработки ошибок |

### Примеры запросов

**Добавить пользователя**

```bash
curl -X POST http://localhost:8080/adduser \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'
```

**Получить пользователя**

```bash
curl http://localhost:8080/user/1
```

## Модуль utils

Функции для прямого использования в скриптах:

| Функция | Описание |
|---------|----------|
| `get_cached(key)` / `set_cached(key, value)` | Потокобезопасный кэш |
| `get_db_connection(db_path)` | Контекстный менеджер для БД |
| `add_user(name, tags)` | Добавить пользователя в users.db |
| `get_user_by_name(name)` | Найти пользователя по имени |
| `store_password(user_id, password)` | Сохранить хеш пароля в файл |
| `set_active(user_id)` / `get_active_users()` | Список активных пользователей |

**Пример**

```python
from utils import add_user, get_user_by_name

uid = add_user("Bob", tags=["admin"])
user = get_user_by_name("Bob")
```

## Базы данных

- **api.py** — `test.db` (таблица `users` с полями `id`, `name`)
- **utils.py** — `users.db` (таблица `users` с полями `id`, `name`, `tags`)

Файлы БД и `passwords.txt` создаются автоматически. Рекомендуется добавить их в `.gitignore`.

## Безопасность

- Параметризованные SQL-запросы (защита от инъекций)
- Хеширование паролей через SHA-256 (для production — bcrypt/argon2)
- Потокобезопасный доступ к общим структурам данных
