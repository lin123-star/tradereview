"""
迁移脚本：给 daily_reviews 表加 vs_rows 字段
直接运行：python migrations/add_vs_rows.py
"""
import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "tradereview.db"


def migrate():
    if not DB_PATH.exists():
        print(f"数据库不存在: {DB_PATH}，跳过迁移（首次启动会自动建表）")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 查现有字段
    cursor.execute("PRAGMA table_info(daily_reviews)")
    existing = {row[1] for row in cursor.fetchall()}

    added = []

    if "vs_rows" not in existing:
        cursor.execute("ALTER TABLE daily_reviews ADD COLUMN vs_rows TEXT DEFAULT '[]'")
        added.append("vs_rows")

    conn.commit()
    conn.close()

    if added:
        print(f"迁移完成，新增字段: {added}")
    else:
        print("字段已存在，无需迁移")


if __name__ == "__main__":
    migrate()
