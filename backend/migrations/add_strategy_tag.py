"""
迁移脚本：
1. 创建 strategies 表
2. 给 trades 表加 strategy_tag_id 字段
直接运行：python migrations/add_strategy_tag.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "tradereview.db"


def migrate():
    if not DB_PATH.exists():
        print("数据库不存在，跳过（首次启动会自动建表）")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 创建 strategies 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            category VARCHAR(30) DEFAULT '',
            description TEXT DEFAULT '',
            entry_signal TEXT DEFAULT '',
            stop_loss_rule TEXT DEFAULT '',
            take_profit_rule TEXT DEFAULT '',
            applicable_market VARCHAR(50) DEFAULT '',
            total_count INTEGER DEFAULT 0,
            win_count INTEGER DEFAULT 0,
            loss_count INTEGER DEFAULT 0,
            win_rate FLOAT DEFAULT 0.0,
            avg_pnl_ratio FLOAT DEFAULT 0.0,
            avg_win_ratio FLOAT DEFAULT 0.0,
            avg_loss_ratio FLOAT DEFAULT 0.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. 给 trades 加 strategy_tag_id
    cursor.execute("PRAGMA table_info(trades)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    added = []
    if "strategy_tag_id" not in existing_cols:
        cursor.execute(
            "ALTER TABLE trades ADD COLUMN strategy_tag_id INTEGER REFERENCES strategies(id)"
        )
        added.append("strategy_tag_id")

    conn.commit()
    conn.close()

    print(f"strategies 表已创建")
    if added:
        print(f"trades 新增字段: {added}")
    else:
        print("trades 字段已存在，无需迁移")


if __name__ == "__main__":
    migrate()