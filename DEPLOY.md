# Развёртывание проекта через Docker Hub

Подробная инструкция: публикация образа в Docker Hub и запуск на сервере.

---

## Часть 1. Подготовка на вашем компьютере (Windows)

### Шаг 1.1. Установка Docker Desktop

1. Скачайте: https://www.docker.com/products/docker-desktop/
2. Запустите установщик, примите условия.
3. Если попросят — включите WSL 2 (для Windows 10/11):
   - Откройте PowerShell от имени администратора
   - Выполните: `wsl --install`
   - Перезагрузите компьютер
4. После установки Docker Desktop перезагрузите ПК.
5. Запустите **Docker Desktop**, дождитесь статуса «Running» (иконка в трее).
6. Откройте PowerShell и проверьте:
   ```powershell
   docker --version
   ```
   Должна отобразиться версия Docker.

### Шаг 1.2. Регистрация на Docker Hub

1. Перейдите на https://hub.docker.com
2. Нажмите **Sign up**.
3. Введите email, логин (например, `myuser`) и пароль.
4. Подтвердите email.
5. Запомните логин — он понадобится для команд ниже (далее: `ВАШ_ЛОГИН`).

---

## Часть 2. Публикация образа в Docker Hub

### Шаг 2.1. Войти в Docker Hub

В PowerShell:

```powershell
docker login
```

- **Username:** ваш логин Docker Hub  
- **Password:** пароль (или Access Token)  
- Успешный вход: `Login Succeeded`

### Шаг 2.2. Перейти в папку проекта

```powershell
cd D:\VSCode\Project\CURSOR
```

### Шаг 2.3. Собрать Docker-образ

```powershell
docker build -t cursor-api .
```

- `-t cursor-api` — имя образа  
- `.` — текущая папка (контекст сборки)  
- Дождитесь окончания сборки (может занять 1–3 минуты).

### Шаг 2.4. Пометить образ для Docker Hub

```powershell
docker tag cursor-api ВАШ_ЛОГИН/cursor-api:latest
```

Пример (логин `ivanov`):

```powershell
docker tag cursor-api ivanov/cursor-api:latest
```

- `ВАШ_ЛОГИН/cursor-api` — путь в Docker Hub  
- `:latest` — тег (версия образа)

### Шаг 2.5. Загрузить образ в Docker Hub

```powershell
docker push ВАШ_ЛОГИН/cursor-api:latest
```

Пример:

```powershell
docker push ivanov/cursor-api:latest
```

Загрузка может занять несколько минут. По завершении образ появится в репозитории:  
https://hub.docker.com/r/ВАШ_ЛОГИН/cursor-api

---

## Часть 3. Запуск на сервере (Linux)

### Шаг 3.1. Подключение к серверу

Подключитесь по SSH:

```powershell
ssh пользователь@IP_СЕРВЕРА
```

Пример:

```powershell
ssh root@192.168.1.100
```

### Шаг 3.2. Установка Docker на сервере (если ещё не установлен)

Для Ubuntu/Debian:

```bash
# Обновление пакетов
sudo apt update

# Установка Docker
sudo apt install -y docker.io

# Добавить текущего пользователя в группу docker
sudo usermod -aG docker $USER

# Выйти и зайти снова (или перезагрузить)
exit
```

После повторного входа проверьте:

```bash
docker --version
```

### Шаг 3.3. Войти в Docker Hub (если образ приватный)

Если образ публичный, этот шаг не нужен.

```bash
docker login
```

### Шаг 3.4. Скачать образ

```bash
docker pull ВАШ_ЛОГИН/cursor-api:latest
```

Пример:

```bash
docker pull ivanov/cursor-api:latest
```

### Шаг 3.5. Запустить контейнер

```bash
docker run -d -p 8080:8080 --name cursor-api --restart unless-stopped ВАШ_ЛОГИН/cursor-api:latest
```

Пример:

```bash
docker run -d -p 8080:8080 --name cursor-api --restart unless-stopped ivanov/cursor-api:latest
```

Параметры:

- `-d` — запуск в фоне  
- `-p 8080:8080` — проброс порта (хост:контейнер)  
- `--name cursor-api` — имя контейнера  
- `--restart unless-stopped` — автозапуск при перезагрузке сервера  

### Шаг 3.6. Проверить работу

```bash
curl http://localhost:8080/user/1
```

Или с другого компьютера в сети:

```
http://IP_СЕРВЕРА:8080/user/1
```

---

## Часть 4. Полезные команды

### На вашем компьютере

| Действие             | Команда                                      |
|----------------------|----------------------------------------------|
| Войти в Docker Hub   | `docker login`                               |
| Собрать образ        | `docker build -t cursor-api .`               |
| Пометить образ       | `docker tag cursor-api ВАШ_ЛОГИН/cursor-api:latest` |
| Загрузить в Hub      | `docker push ВАШ_ЛОГИН/cursor-api:latest`    |

### На сервере

| Действие                | Команда                                      |
|-------------------------|----------------------------------------------|
| Скачать образ           | `docker pull ВАШ_ЛОГИН/cursor-api:latest`    |
| Запустить контейнер     | `docker run -d -p 8080:8080 --name cursor-api --restart unless-stopped ВАШ_ЛОГИН/cursor-api:latest` |
| Посмотреть контейнеры   | `docker ps`                                  |
| Остановить              | `docker stop cursor-api`                     |
| Удалить контейнер       | `docker rm -f cursor-api`                    |
| Обновить (новая версия) | `docker pull ВАШ_ЛОГИН/cursor-api:latest` <br> `docker rm -f cursor-api` <br> `docker run -d -p 8080:8080 --name cursor-api --restart unless-stopped ВАШ_ЛОГИН/cursor-api:latest` |

---

## Часть 5. Обновление образа

После изменений в коде:

**На компьютере:**

```powershell
cd D:\VSCode\Project\CURSOR
docker build -t cursor-api .
docker tag cursor-api ВАШ_ЛОГИН/cursor-api:latest
docker push ВАШ_ЛОГИН/cursor-api:latest
```

**На сервере:**

```bash
docker pull ВАШ_ЛОГИН/cursor-api:latest
docker rm -f cursor-api
docker run -d -p 8080:8080 --name cursor-api --restart unless-stopped ВАШ_ЛОГИН/cursor-api:latest
```

---

## Часть 6. Проверка с вашего ПК

```powershell
python check_endpoints.py http://IP_СЕРВЕРА:8080
```

Замените `IP_СЕРВЕРА` на IP-адрес сервера (например, `192.168.1.100`).

---

## Часть 7. Firewall (если порт недоступен извне)

На сервере с UFW (Ubuntu):

```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

Для облачных провайдеров (AWS, DigitalOcean и т.п.) настройте Security Group / Firewall: разрешить входящий трафик на порт 8080.
