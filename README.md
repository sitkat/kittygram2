# Kittygram2

REST API для управления котиками: добавление, просмотр, редактирование питомцев, их достижений и владельцев. Построен на Django REST Framework с JWT-аутентификацией.

## Стек технологий

- Python 3.11
- Django 3.2.3
- Django REST Framework 3.12.4
- Djoser 2.1.0 (управление пользователями)
- Simple JWT 4.8.0 (JWT-аутентификация)
- SQLite (база данных по умолчанию)
- Docker / Docker Compose

## Зависимости

Перечень зависимостей находится в файле `requirements.txt`:

| Пакет | Версия |
|---|---|
| Django | 3.2.3 |
| djangorestframework | 3.12.4 |
| PyJWT | 2.1.0 |
| djangorestframework-simplejwt | 4.8.0 |
| djoser | 2.1.0 |

## Как запустить проект локально

### 1. Клонировать репозиторий

```bash
git clone https://github.com/sitkat/kittygram2.git
cd kittygram2
```

### 2. Настроить переменные окружения

Скопировать файл `.env.example` в `.env` и при необходимости изменить значения:

```bash
cp .env.example .env
```

### 3. Запуск через Docker Compose

```bash
docker compose up --build
```

Приложение будет доступно по адресу: http://localhost:8000/

### 4. Запуск без Docker (локально)

Создать и активировать виртуальное окружение:

```bash
python3 -m venv env
source env/bin/activate  # Linux/macOS
# env\Scripts\activate   # Windows
```

Обновить pip и установить зависимости:

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Выполнить миграции:

```bash
python3 manage.py migrate
```

Запустить сервер разработки:

```bash
python3 manage.py runserver
```

Приложение будет доступно по адресу: http://127.0.0.1:8000/

## API эндпоинты

| Путь | Описание |
|---|---|
| `/cats/` | CRUD для котиков |
| `/users/` | Список пользователей |
| `/achievements/` | CRUD для достижений |
| `/auth/users/` | Регистрация (Djoser) |
| `/auth/jwt/create/` | Получение JWT-токена |
| `/auth/jwt/refresh/` | Обновление JWT-токена |
| `/admin/` | Админ-панель Django |

## Автор

Проект создан в рамках обучения на Яндекс.Практикум.
