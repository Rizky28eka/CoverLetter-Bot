import sqlite3
import pytest
from unittest.mock import patch
import importlib
import os
from src import history_manager


@pytest.fixture
def temp_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            file_path TEXT NOT NULL
        )
    """)
    conn.commit()
    yield conn
    conn.close()


def test_init_db(temp_db):
    # The fixture already initializes the database, so we just check if the table exists
    cursor = temp_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='applications'")
    assert cursor.fetchone() is not None


def test_save_and_load_history():
    # Override the DB_FILE constant to use the in-memory database
    if os.path.exists(history_manager.DB_FILE):
        os.remove(history_manager.DB_FILE)
        
    with patch("src.history_manager.DB_FILE", ":memory:"):
        importlib.reload(history_manager)
        history_manager.init_db()
        history_manager.save_application("Test Corp", "Software Engineer", "/path/to/file")
        history = history_manager.load_history()

        assert len(history) == 1
        assert history[0]["company"] == "Test Corp"
        assert history[0]["position"] == "Software Engineer"
        assert history[0]["file_path"] == "/path/to/file"
