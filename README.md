# CURSOR — API и утилиты для пользователей

Flask-приложение для управления пользователями с SQLite, потокобезопасными операциями и безопасной работой с паролями.

Реализации: **Python (Flask)** и **Go** — см. [server-go/](server-go/).

## Структура проекта

```
CURSOR/
├── api.py            # Flask API (REST-эндпоинты)
├── utils.py          # Утилиты (БД, кэш, пароли)
├── requirements.txt
├── check_endpoints.py # Скрипт проверки API
├── Dockerfile
├── .dockerignore
├── openapi.yaml      # OpenAPI 3.1 спецификация
├── DEPLOY.md         # Инструкция по Docker Hub и развёртыванию
├── server-go/        # Go-реализация API
└── README.md
```

## Быстрый старт

### Python

```bash
# Установка
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt

# Запуск
python api.py
```

### Docker

```bash
docker build -t cursor-api .
docker run -p 8080:8080 cursor-api
```

API: `http://localhost:8080`

## Установка (Python)

- **Требования:** Python 3.10+

```bash
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Запуск

```bash
python api.py
```

Сервер: `http://0.0.0.0:8080`

## Docker

```bash
# Локально
docker build -t cursor-api .
docker run -p 8080:8080 cursor-api

# На сервере (в фоне)
docker run -d -p 8080:8080 --name cursor-api cursor-api
```

**Публикация в Docker Hub и развёртывание** — [DEPLOY.md](DEPLOY.md).

## Проверка эндпоинтов

```bash
# Сначала запустите API: python api.py
python check_endpoints.py
python check_endpoints.py http://192.168.1.100:8080  # с другим URL
```

Проверяет: POST /adduser, GET /user, 404, /activate, /slow, /wrong, валидация 400.

## API

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/adduser` | Добавить пользователя |
| GET | `/user/<id>` | Получить пользователя по ID |
| GET | `/activate/<uid>` | Добавить uid в активные (асинхронно) |
| GET | `/slow` | Тяжёлые вычисления |
| GET | `/wrong` | Пример обработки ошибок |

**OpenAPI 3.1:** [openapi.yaml](openapi.yaml) — для Swagger UI, Redoc, генерации клиентов.

## Модуль utils

| Функция | Описание |
|---------|----------|
| `get_cached` / `set_cached` | Потокобезопасный кэш |
| `get_db_connection(db_path)` | Контекстный менеджер для БД |
| `add_user(name, tags)` | Добавить пользователя в users.db |
| `get_user_by_name(name)` | Найти пользователя по имени |
| `store_password(user_id, password)` | Сохранить хеш пароля |
| `set_active` / `get_active_users` | Список активных пользователей |

```python
from utils import add_user, get_user_by_name
uid = add_user("Bob", tags=["admin"])
user = get_user_by_name("Bob")
```

## Базы данных

- **api.py** — `test.db` (таблица `users`: id, name)
- **utils.py** — `users.db` (таблица `users`: id, name, tags)

## Go-реализация

В каталоге [server-go/](server-go/) — эквивалентный API на Go. Требуется Go 1.21+.

```bash
cd server-go
go mod download
go run .
```

## Безопасность

- Параметризованные SQL-запросы
- Хеширование паролей (SHA-256; для production — bcrypt/argon2)
- Потокобезопасный доступ к общим данным
