import json
import os
from datetime import datetime

HISTORY_FILE = "application_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Peringatan: File riwayat {HISTORY_FILE} rusak. Membuat yang baru.")
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"Error menyimpan riwayat: {e}")

def add_to_history(company, position, file_path):
    history = load_history()
    new_entry = {
        "timestamp": datetime.now().isoformat(),
        "company": company,
        "position": position,
        "file_path": file_path
    }
    history.append(new_entry)
    save_history(history)
    print(f"Riwayat lamaran ditambahkan: {company} - {position}")
