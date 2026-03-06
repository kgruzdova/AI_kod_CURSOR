"""
Утилиты для работы с пользователями.
Безопасная работа с БД, хеширование паролей, потокобезопасный кэш.
"""
import sqlite3
import threading
import json
from contextlib import contextmanager
from typing import Optional

try:
    import hashlib
    _HASHLIB = True
except ImportError:
    _HASHLIB = False


# --- Потокобезопасный кэш ---
_cache: dict = {}
_cache_lock = threading.Lock()


def get_cached(key: str):
    """Получить значение из кэша."""
    with _cache_lock:
        return _cache.get(key)


def set_cached(key: str, value) -> None:
    """Сохранить значение в кэш."""
    with _cache_lock:
        _cache[key] = value


# --- Контекстный менеджер для БД ---
@contextmanager
def get_db_connection(db_path: str = 'users.db'):
    """Гарантирует закрытие соединения с БД при любом исходе."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# --- Безопасная работа с пользователями ---
def add_user(name: str, tags: Optional[list] = None) -> int:
    """
    Добавляет пользователя в локальную базу.
    Возвращает id (int) нового пользователя.
    """
    tags = list(tags) if tags is not None else []
    tags.append("new")

    with get_db_connection() as conn:
        cur = conn.cursor()
        # Параметризованный запрос — защита от SQL-инъекций
        cur.execute(
            "INSERT INTO users (name, tags) VALUES (?, ?)",
            (name, json.dumps(tags))
        )
        return cur.lastrowid


def get_user_by_name(name: str) -> Optional[dict]:
    """
    Получить пользователя по имени.
    Возвращает dict или None, если не найден.
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, tags FROM users WHERE name = ?", (name,))
        row = cur.fetchone()

    if not row:
        return None

    uid, uname, tags_json = row
    tags = tags_json
    if isinstance(tags_json, str):
        try:
            tags = json.loads(tags_json)
        except json.JSONDecodeError:
            tags = []

    return {"id": uid, "name": uname, "tags": tags}


# --- Безопасное хранение паролей ---
def _hash_password(password: str) -> str:
    """Хеширование пароля (SHA-256). Для production рекомендуется bcrypt/argon2."""
    if _HASHLIB:
        return hashlib.sha256(password.encode()).hexdigest()
    raise RuntimeError("hashlib недоступен — безопасное хеширование невозможно")


def store_password(user_id, password: str) -> None:
    """Сохраняет хеш пароля в файл. Файл всегда закрывается корректно."""
    hashed = _hash_password(password)
    with open('passwords.txt', 'a', encoding='utf-8') as f:
        f.write(f"{user_id}:{hashed}\n")


# --- Потокобезопасный список активных пользователей ---
_active_users: list = []
_active_lock = threading.Lock()


def set_active(user_id) -> None:
    """Добавляет пользователя в список активных. Потокобезопасно."""
    with _active_lock:
        _active_users.append(user_id)
        if len(_active_users) > 5:
            _active_users.pop(0)


def get_active_users() -> list:
    """Возвращает копию списка активных пользователей."""
    with _active_lock:
        return list(_active_users)
