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
            score INTEGER DEFAULT 0,
            rationale TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Adiciona colunas se não existirem (para migração simples)
    try:
        cursor.execute("ALTER TABLE opportunities ADD COLUMN score INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE opportunities ADD COLUMN rationale TEXT")
    except sqlite3.OperationalError:
        pass # Colunas já existem
        
    conn.commit()
    conn.close()

def init_user_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id TEXT PRIMARY KEY,
            gemini_key TEXT,
            openrouter_key TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user_key(user_id, service, key):
    init_user_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    user_id = str(user_id)
    if service == "gemini":
        cursor.execute("INSERT INTO user_settings (user_id, gemini_key) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET gemini_key=?", (user_id, key, key))
    else:
        cursor.execute("INSERT INTO user_settings (user_id, openrouter_key) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET openrouter_key=?", (user_id, key, key))
    conn.commit()
    conn.close()

def get_user_keys(user_id):
    init_user_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT gemini_key, openrouter_key FROM user_settings WHERE user_id = ?", (str(user_id),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def save_opportunity(data):
    if not isinstance(data, list): data = [data]
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    saved = 0
    for item in data:
        try:
            cursor.execute('''
                INSERT INTO opportunities (title, url, description, source, type, score, rationale)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('title'), 
                item.get('url'), 
                item.get('description'), 
                item.get('source'), 
                item.get('type'),
                item.get('score', 0),
                item.get('rationale', '')
            ))
            saved += 1
        except sqlite3.IntegrityError:
            # Se já existe, opcionalmente podemos atualizar o score/rationale se for maior
            continue
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