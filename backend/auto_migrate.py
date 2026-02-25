"""
自动数据库迁移脚本。
每次启动时运行，检测缺失的列/表并自动补齐，不会丢失已有数据。
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'shu_prophet.db')


def get_table_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def migrate():
    if not os.path.exists(DB_PATH):
        print("[migrate] 数据库不存在，跳过迁移（将由 db.create_all 创建）")
        return

    print(f"[migrate] 检测数据库: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 1. user 表：补 credits 列 ---
    if table_exists(cursor, 'user'):
        cols = get_table_columns(cursor, 'user')
        if 'credits' not in cols:
            print("[migrate] user 表添加 credits 列")
            cursor.execute("ALTER TABLE user ADD COLUMN credits INTEGER DEFAULT 0")

    # --- 2. 新增表 ---
    if not table_exists(cursor, 'redeem_code'):
        print("[migrate] 创建 redeem_code 表")
        cursor.execute("""
            CREATE TABLE redeem_code (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(64) UNIQUE NOT NULL,
                credits INTEGER NOT NULL,
                is_used BOOLEAN DEFAULT 0,
                used_by INTEGER REFERENCES user(id),
                created_at DATETIME,
                used_at DATETIME
            )
        """)

    if not table_exists(cursor, 'daily_usage'):
        print("[migrate] 创建 daily_usage 表")
        cursor.execute("""
            CREATE TABLE daily_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES user(id),
                date VARCHAR(10) NOT NULL,
                chat_count INTEGER DEFAULT 0,
                UNIQUE(user_id, date)
            )
        """)

    if not table_exists(cursor, 'credit_log'):
        print("[migrate] 创建 credit_log 表")
        cursor.execute("""
            CREATE TABLE credit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES user(id),
                amount INTEGER NOT NULL,
                type VARCHAR(20) NOT NULL,
                description VARCHAR(200) DEFAULT '',
                created_at DATETIME
            )
        """)

    conn.commit()
    conn.close()
    print("[migrate] 迁移完成")


if __name__ == '__main__':
    migrate()
