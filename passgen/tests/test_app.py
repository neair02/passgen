"""
Тесты для приложения PassVault.
Запуск: pytest tests/ -v
"""
import os
import sys
import sqlite3
import tempfile

import pytest

_db_fd, _db_path = tempfile.mkstemp(suffix='.db')
os.environ['DATABASE'] = _db_path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app as flask_app, validate_password_entry


def _reset():
    con = sqlite3.connect(_db_path)
    con.execute("DROP TABLE IF EXISTS passwords")
    con.execute("""
        CREATE TABLE passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            login TEXT DEFAULT '',
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT (datetime('now','localtime'))
        )
    """)
    con.commit()
    con.close()


def _insert(label, login, password):
    con = sqlite3.connect(_db_path)
    con.execute(
        "INSERT INTO passwords (label, login, password) VALUES (?, ?, ?)",
        (label, login, password)
    )
    con.commit()
    con.close()


@pytest.fixture(autouse=True)
def clean_db():
    _reset()


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c


# ── 1. Тест главной страницы ──────────────────────────────────────────────────

def test_index_returns_200(client):
    """Главная страница должна отвечать кодом 200."""
    assert client.get('/').status_code == 200


# ── 2. Тест добавления объекта ────────────────────────────────────────────────

def test_save_password_appears_in_db(client):
    """Сохранённый пароль должен появляться в хранилище."""
    client.post('/save', data={'label': 'GitHub', 'login': 'testuser', 'password': 'Pass123!'})
    con = sqlite3.connect(_db_path)
    row = con.execute("SELECT * FROM passwords WHERE label='GitHub'").fetchone()
    con.close()
    assert row is not None
    assert row[3] == 'Pass123!'


# ── 3. Тест поиска / фильтрации ───────────────────────────────────────────────

def test_search_returns_only_matching(client):
    """Поиск должен возвращать только подходящие записи."""
    _insert('GitLab', '', 'pass1')
    _insert('Amazon', '', 'pass2')
    r = client.get('/?q=GitLab')
    assert b'GitLab' in r.data
    assert b'Amazon' not in r.data


# ── 4. Тест обработки 404 ─────────────────────────────────────────────────────

def test_edit_nonexistent_returns_404(client):
    """Редактирование несуществующей записи должно возвращать 404."""
    assert client.get('/edit/99999').status_code == 404


def test_delete_nonexistent_returns_404(client):
    """Удаление несуществующей записи должно возвращать 404."""
    assert client.post('/delete/99999').status_code == 404


# ── 5. Тест на корректность данных (валидация) ────────────────────────────────

def test_validate_rejects_empty_label():
    assert validate_password_entry('', 'password123') is False


def test_validate_rejects_empty_password():
    assert validate_password_entry('GitHub', '') is False


def test_validate_rejects_whitespace_only():
    assert validate_password_entry('   ', '   ') is False


def test_validate_accepts_valid_data():
    assert validate_password_entry('GitHub', 'StrongPass1!') is True


# ── Дополнительный тест: генератор ───────────────────────────────────────────

def test_generate_returns_password_of_correct_length(client):
    """Генератор должен возвращать JSON с паролем нужной длины."""
    r = client.post('/generate', data={'length': '20', 'upper': 'on', 'digits': 'on'})
    assert r.status_code == 200
    data = r.get_json()
    assert 'password' in data
    assert len(data['password']) == 20
