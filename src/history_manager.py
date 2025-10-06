import sqlite3
from datetime import datetime
from typing import Any, Dict, List

DB_FILE: str = "application_history.db"


def init_db() -> None:
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(DB_FILE)
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
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()


def save_application(company: str, position: str, file_path: str) -> None:
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        timestamp: str = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO applications (timestamp, company, position, file_path)
            VALUES (?, ?, ?, ?)
        """,
            (timestamp, company, position, file_path),
        )
        conn.commit()
        print(f"Riwayat lamaran disimpan ke DB: {company} - {position}")
    except sqlite3.Error as e:
        print(f"Error saving application to database: {e}")
    finally:
        if conn:
            conn.close()


def load_history() -> List[Dict[str, Any]]:
    conn: sqlite3.Connection | None = None
    history: List[Dict[str, Any]] = []
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, company, position, file_path FROM applications ORDER BY timestamp DESC"
        )
        rows = cursor.fetchall()
        for row in rows:
            history.append(
                {
                    "timestamp": row[0],
                    "company": row[1],
                    "position": row[2],
                    "file_path": row[3],
                }
            )
    except sqlite3.Error as e:
        print(f"Error loading history from database: {e}")
    finally:
        if conn:
            conn.close()
    return history


# Panggil init_db saat modul diimpor
init_db()
