# Server-Go — API на Golang

Go-версия API для управления пользователями. Функциональность эквивалентна Python-реализации (api.py).

## Структура проекта

```
server-go/
├── main.go           # Точка входа
├── models/           # Модели данных
│   └── user.go
├── db/               # Работа с БД
│   └── db.go
├── handlers/         # HTTP-обработчики
│   ├── users.go      # пользователи
│   ├── active.go     # активные uid
│   └── demo.go       # slow, wrong
├── router/           # Маршрутизация
│   └── router.go
├── util/             # Утилиты (ответы, JSON)
│   └── response.go
├── go.mod
└── README.md
```

## Требования

- Go 1.21+

## Установка

```bash
cd server-go
go mod download
```

## Запуск

```bash
go run main.go
```

Сервер будет доступен по адресу `http://0.0.0.0:8080`.

Сборка исполняемого файла:

```bash
go build -o server .
./server          # Linux/macOS
server.exe        # Windows
```

## API

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/adduser` | Добавить пользователя (JSON: `{"name": "..."}`) |
| GET | `/user/<id>` | Получить пользователя по ID |
| GET | `/activate/<uid>` | Добавить uid в список активных (асинхронно) |
| GET | `/slow` | Тяжёлые вычисления |
| GET | `/wrong` | Пример обработки ошибок (деление на ноль) |

## Примеры

**Добавить пользователя**

```bash
# Windows (cmd)
curl -X POST http://localhost:8080/adduser -H "Content-Type: application/json" -d "{\"name\": \"Alice\"}"

# Linux/macOS
curl -X POST http://localhost:8080/adduser \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'
```

**Получить пользователя**

```bash
curl http://localhost:8080/user/1
```

**Список активных (после вызова /activate/foo)**

```bash
curl http://localhost:8080/activate/foo
```

## База данных

Используется SQLite. Файл `test.db` создаётся автоматически в текущей директории при первом запуске. Таблица `users` с полями `id`, `name`.

## Сборка под разные платформы

```bash
# Windows
GOOS=windows GOARCH=amd64 go build -o server.exe .

# Linux
GOOS=linux GOARCH=amd64 go build -o server .

# macOS (Apple Silicon)
GOOS=darwin GOARCH=arm64 go build -o server .
```
