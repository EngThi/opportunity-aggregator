import sqlite3
import os

# Caminho absoluto para evitar problemas no Docker
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Tenta usar a pasta /data se existir (Docker), senão usa a raiz
DATA_DIR = "/app/data" if os.path.exists("/app/data") else BASE_DIR
DB_PATH = os.path.join(DATA_DIR, "opportunities.db")

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
            openrouter_key TEXT,
            profile_md TEXT,
            preferred_model TEXT
        )
    ''')
    # Migration: Ensure new columns exist
    try:
        cursor.execute("ALTER TABLE user_settings ADD COLUMN profile_md TEXT")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE user_settings ADD COLUMN preferred_model TEXT")
    except sqlite3.OperationalError: pass
    
    conn.commit()
    conn.close()

def save_user_model(user_id, model_name):
    init_user_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_settings (user_id, preferred_model) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET preferred_model=?", (str(user_id), model_name, model_name))
    conn.commit()
    conn.close()

def save_user_profile(user_id, profile_md):
    init_user_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_settings (user_id, profile_md) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET profile_md=?", (str(user_id), profile_md, profile_md))
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
    cursor.execute("SELECT gemini_key, openrouter_key, profile_md, preferred_model FROM user_settings WHERE user_id = ?", (str(user_id),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def clear_user_setting(user_id, setting):
    """Deleta uma configuração específica do usuário ou tudo"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    user_id = str(user_id)
    
    if setting == "gemini":
        cursor.execute("UPDATE user_settings SET gemini_key = NULL WHERE user_id = ?", (user_id,))
    elif setting == "openrouter":
        cursor.execute("UPDATE user_settings SET openrouter_key = NULL WHERE user_id = ?", (user_id,))
    elif setting == "profile":
        cursor.execute("UPDATE user_settings SET profile_md = NULL WHERE user_id = ?", (user_id,))
    elif setting == "model":
        cursor.execute("UPDATE user_settings SET preferred_model = NULL WHERE user_id = ?", (user_id,))
    elif setting == "all":
        cursor.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
        
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

def get_latest_opportunities(limit=10):
    """Retorna as últimas oportunidades salvas"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM opportunities ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_opportunity_by_id(opp_id):
    """Busca uma oportunidade específica pelo ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

init_db()