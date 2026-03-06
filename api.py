"""
Flask API для управления пользователями.
Безопасная работа с БД, потокобезопасность, корректная обработка ошибок.
"""
from flask import Flask, request, jsonify
import sqlite3
import time
import threading
from contextlib import contextmanager

app = Flask(__name__)

DB_PATH = "test.db"


@contextmanager
def get_db():
    """Контекстный менеджер для работы с БД. Гарантирует закрытие соединения."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _init_db():
    """Создание таблицы users при первом запуске."""
    with get_db() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)"
        )


_init_db()


# --- Эндпоинты пользователей ---
@app.route("/adduser", methods=["POST"])
def add_user():
    """Добавить пользователя. Параметризованный запрос — защита от SQL-инъекций."""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (name) VALUES (?)", (name,))
        return jsonify({"status": "ok"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/user/<int:uid>")
def get_user(uid):
    """Получить пользователя по ID. Возвращает 404 если не найден."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM users WHERE id = ?", (uid,))
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": row[0], "name": row[1]}), 200


# --- Потокобезопасный список активных ---
_active = []
_active_lock = threading.Lock()


@app.route("/activate/<uid>")
def activate(uid):
    """Добавляет uid в список активных в фоновом потоке. Потокобезопасно."""
    def worker():
        time.sleep(0.5)
        with _active_lock:
            _active.append(uid)
            if len(_active) > 3:
                _active.pop(0)

    threading.Thread(target=worker, daemon=True).start()

    with _active_lock:
        active_copy = list(_active)
    return jsonify({"status": "processing", "active": active_copy}), 202


# --- Тяжёлый эндпоинт (выполняется в потоке, не блокирует другие запросы) ---
@app.route("/slow")
def slow():
    """Тяжёлые вычисления. В production — вынести в Celery/RQ."""
    result = [None]

    def compute():
        x = 0
        for i in range(1_000_000):
            for j in range(100):
                x += i * j
        result[0] = str(x)

    t = threading.Thread(target=compute)
    t.start()
    t.join()
    return result[0]


# --- Эндпоинт с корректной обработкой ошибок ---
@app.route("/wrong")
def wrong():
    """Пример правильной обработки исключений."""
    try:
        a = 10 / 0
        return jsonify({"msg": "ok", "data": a}), 200
    except ZeroDivisionError as e:
        return jsonify({"msg": "error", "error": str(e)}), 500


if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
