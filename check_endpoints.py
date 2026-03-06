#!/usr/bin/env python3
"""
Скрипт проверки всех эндпоинтов API.
Использование: python check_endpoints.py [BASE_URL]
Пример: python check_endpoints.py http://localhost:8080
"""
import json
import sys
import urllib.request
import urllib.error

DEFAULT_URL = "http://localhost:8080"


def request(method: str, url: str, body: dict | None = None) -> tuple[int, str | dict]:
    """Выполняет HTTP-запрос, возвращает (status_code, body)."""
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if body else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw
    except urllib.error.URLError as e:
        reason = str(e.reason).lower()
        errno = getattr(getattr(e, "reason", None), "errno", None)
        if errno == 10061 or "refused" in reason or "10061" in reason:
            print("Ошибка: сервер API не запущен.")
            print("Сначала запустите API в другом терминале: python api.py")
            print("Затем снова выполните: python check_endpoints.py")
        else:
            print(f"Ошибка подключения: {e.reason}")
        sys.exit(1)


def check(name: str, ok: bool, status: int, body) -> None:
    """Выводит результат проверки."""
    icon = "✓" if ok else "✗"
    print(f"  {icon} {name}: HTTP {status} -> {body}")


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print(f"Проверка API: {base}\n")

    # 1. POST /adduser
    print("1. POST /adduser")
    status, body = request("POST", f"{base}/adduser", {"name": "TestUser"})
    ok = status == 201 and (isinstance(body, dict) and body.get("status") == "ok")
    check("Создание пользователя", ok, status, body)

    # 2. GET /user/1
    print("\n2. GET /user/1")
    status, body = request("GET", f"{base}/user/1")
    ok = status == 200 and isinstance(body, dict) and "id" in body and "name" in body
    check("Получение пользователя по ID", ok, status, body)

    # 3. GET /user/99999 (404)
    print("\n3. GET /user/99999 (ожидаем 404)")
    status, body = request("GET", f"{base}/user/99999")
    ok = status == 404
    check("Несуществующий пользователь → 404", ok, status, body)

    # 4. GET /activate/foo
    print("\n4. GET /activate/foo")
    status, body = request("GET", f"{base}/activate/foo")
    ok = status == 202 and isinstance(body, dict) and body.get("status") == "processing"
    check("Активация uid", ok, status, body)

    # 5. GET /slow
    print("\n5. GET /slow")
    status, body = request("GET", f"{base}/slow")
    ok = status == 200 and (isinstance(body, str) and body.replace("-", "").isdigit())
    check("Тяжёлые вычисления", ok, status, body[:30] + "..." if len(str(body)) > 30 else body)

    # 6. GET /wrong
    print("\n6. GET /wrong (ожидаем 500)")
    status, body = request("GET", f"{base}/wrong")
    ok = status == 500 and isinstance(body, dict) and "error" in body
    check("Обработка ошибки", ok, status, body)

    # 7. POST /adduser без name (400)
    print("\n7. POST /adduser без name (ожидаем 400)")
    status, body = request("POST", f"{base}/adduser", {"name": ""})
    ok = status == 400
    check("Валидация пустого имени", ok, status, body)

    print("\n--- Готово ---")


if __name__ == "__main__":
    main()
