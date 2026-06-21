# 🔐 PassVault — Генератор и хранилище паролей

Веб-приложение на Flask для генерации надёжных паролей и их удобного хранения.

## Возможности

- Генерация пароля с настройкой длины (4–64 символа), заглавных букв, цифр и спецсимволов
- Сохранение паролей с меткой (сайт) и логином
- Пароли скрыты звёздочками, показываются по кнопке 👁
- Поиск по метке и логину
- Редактирование и удаление записей
- Тёмный интерфейс в стиле GitHub

## Технологии

| Слой | Технология |
|------|-----------|
| Backend | Python 3.11 · Flask 3.x |
| База данных | SQLite (через стандартный `sqlite3`) |
| Frontend | HTML5 · CSS (без фреймворков) · Vanilla JS |
| Тесты | pytest |

## Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://gitee.com/YOUR_USERNAME/passvault.git
cd passvault

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить приложение
python app.py
```

Откройте браузер: **http://127.0.0.1:5000**

## Запуск тестов

```bash
pytest tests/ -v
```

## Маршруты

| Метод | URL | Описание |
|-------|-----|---------|
| GET | `/` | Главная: генератор + список паролей |
| POST | `/generate` | API: генерация пароля (JSON) |
| POST | `/save` | Сохранение пароля в БД |
| GET | `/edit/<id>` | Форма редактирования |
| POST | `/edit/<id>` | Применить изменения |
| POST | `/delete/<id>` | Удалить запись |

## Структура проекта

```
passvault/
├── app.py              # Основное Flask-приложение
├── database.py         # Работа с SQLite
├── requirements.txt
├── README.md
├── docs/
│   ├── requirements.md   # Требования к системе
│   ├── architecture.md   # Архитектура
│   └── user_guide.md     # Руководство пользователя
├── templates/
│   ├── index.html
│   ├── edit.html
│   └── 404.html
├── static/css/
│   └── style.css
└── tests/
    └── test_app.py
```

---
Учебный проект · ТРПО 2026 · ИС202к
