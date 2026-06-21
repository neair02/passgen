import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import init_db, get_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')


@app.before_request
def setup():
    init_db()


# ── Маршруты ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Главная страница — генератор + список сохранённых паролей."""
    search = request.args.get('q', '').strip()
    db = get_db()
    if search:
        rows = db.execute(
            "SELECT * FROM passwords WHERE label LIKE ? OR login LIKE ? ORDER BY created_at DESC",
            (f'%{search}%', f'%{search}%')
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM passwords ORDER BY created_at DESC"
        ).fetchall()
    return render_template('index.html', passwords=rows, search=search)


@app.route('/generate', methods=['POST'])
def generate():
    """API-эндпоинт: генерирует пароль по параметрам и возвращает JSON."""
    length = int(request.form.get('length', 16))
    length = max(4, min(length, 128))

    use_digits = request.form.get('digits') == 'on'
    use_special = request.form.get('special') == 'on'
    use_upper = request.form.get('upper') == 'on'

    chars = string.ascii_lowercase
    required = []

    if use_upper:
        chars += string.ascii_uppercase
        required.append(random.choice(string.ascii_uppercase))
    if use_digits:
        chars += string.digits
        required.append(random.choice(string.digits))
    if use_special:
        special_chars = '!@#$%^&*()-_=+[]{}|;:,.<>?'
        chars += special_chars
        required.append(random.choice(special_chars))

    # Заполняем оставшиеся символы
    remaining = length - len(required)
    password = required + [random.choice(chars) for _ in range(remaining)]
    random.shuffle(password)
    password = ''.join(password)

    return jsonify({'password': password})


@app.route('/save', methods=['POST'])
def save():
    """Сохраняет пароль в базу данных."""
    label = request.form.get('label', '').strip()
    login = request.form.get('login', '').strip()
    password = request.form.get('password', '').strip()

    if not label:
        flash('Укажите метку (название сайта или сервиса)', 'error')
        return redirect(url_for('index'))
    if not password:
        flash('Пароль не может быть пустым', 'error')
        return redirect(url_for('index'))

    db = get_db()
    db.execute(
        "INSERT INTO passwords (label, login, password) VALUES (?, ?, ?)",
        (label, login, password)
    )
    db.commit()
    flash(f'Пароль для «{label}» сохранён', 'success')
    return redirect(url_for('index'))


@app.route('/edit/<int:pwd_id>', methods=['GET', 'POST'])
def edit(pwd_id):
    """Редактирование сохранённого пароля."""
    db = get_db()
    row = db.execute("SELECT * FROM passwords WHERE id = ?", (pwd_id,)).fetchone()
    if row is None:
        return render_template('404.html'), 404

    if request.method == 'POST':
        label = request.form.get('label', '').strip()
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()

        if not label:
            flash('Метка обязательна', 'error')
            return render_template('edit.html', pwd=row)
        if not password:
            flash('Пароль не может быть пустым', 'error')
            return render_template('edit.html', pwd=row)

        db.execute(
            "UPDATE passwords SET label=?, login=?, password=? WHERE id=?",
            (label, login, password, pwd_id)
        )
        db.commit()
        flash('Изменения сохранены', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', pwd=row)


@app.route('/delete/<int:pwd_id>', methods=['POST'])
def delete(pwd_id):
    """Удаление пароля."""
    db = get_db()
    row = db.execute("SELECT label FROM passwords WHERE id = ?", (pwd_id,)).fetchone()
    if row is None:
        return render_template('404.html'), 404

    db.execute("DELETE FROM passwords WHERE id = ?", (pwd_id,))
    db.commit()
    flash(f'Пароль для «{row["label"]}» удалён', 'success')
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


# Утилита валидации (используется в тестах)
def validate_password_entry(label: str, password: str) -> bool:
    """Возвращает True если данные корректны."""
    return bool(label.strip()) and bool(password.strip())


if __name__ == '__main__':
    app.run(debug=True)
