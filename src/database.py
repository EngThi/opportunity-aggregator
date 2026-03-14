import sqlite3
import os

DB_PATH = "opportunities.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            description TEXT,
            source TEXT,
            type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_opportunity(data):
    if not isinstance(data, list): data = [data]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    saved = 0
    for item in data:
        try:
            cursor.execute('''
                INSERT INTO opportunities (title, url, description, source, type)
                VALUES (?, ?, ?, ?, ?)
            ''', (item['title'], item['url'], item['description'], item['source'], item['type']))
            saved += 1
        except sqlite3.IntegrityError:
            continue # Duplicado
    conn.commit()
    conn.close()
    return saved

def get_today_opportunities():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM opportunities WHERE date(created_at) = date('now')")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_opportunities(keyword):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM opportunities WHERE title LIKE ? OR description LIKE ?", (f'%{keyword}%', f'%{keyword}%'))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

init_db()
