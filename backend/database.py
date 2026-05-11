import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "prompts.db"))

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn

def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            scenario TEXT NOT NULL,
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            output_type TEXT NOT NULL,
            preview_images TEXT DEFAULT '[]',
            trend_score REAL DEFAULT 50.0,
            usage_count INTEGER DEFAULT 0,
            source TEXT DEFAULT 'crawler',
            collection_folder TEXT DEFAULT '默认',
            user_id INTEGER REFERENCES users(id),
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            keyword TEXT NOT NULL,
            heat REAL DEFAULT 0.0,
            source TEXT DEFAULT 'builtin',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS import_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            row_count INTEGER DEFAULT 0,
            trends_extracted INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category);
        CREATE INDEX IF NOT EXISTS idx_prompts_scenario ON prompts(scenario);
        CREATE INDEX IF NOT EXISTS idx_prompts_trend_score ON prompts(trend_score DESC);
        CREATE INDEX IF NOT EXISTS idx_trends_category ON trends(category);
        CREATE INDEX IF NOT EXISTS idx_trends_heat ON trends(heat DESC);
    """)
    # 迁移：为旧数据库添加 collection_folder 列
    try:
        conn.execute("ALTER TABLE prompts ADD COLUMN collection_folder TEXT DEFAULT '默认'")
    except sqlite3.OperationalError:
        pass
    # 迁移：为旧数据库添加 user_id 列
    try:
        conn.execute("ALTER TABLE prompts ADD COLUMN user_id INTEGER REFERENCES users(id)")
    except sqlite3.OperationalError:
        pass
    # 迁移：添加 user_id 索引
    try:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_prompts_user_id ON prompts(user_id)")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()
