import sqlite3

def init_walnut_tea_db():
    conn = sqlite3.connect('tea_vault.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        stock_grams REAL NOT NULL,
        location TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teaware (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        material TEXT NOT NULL,
        capacity_ml INTEGER NOT NULL,
        status TEXT DEFAULT '在用'
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tea_id INTEGER,
        teaware_id INTEGER,
        water_temp INTEGER,
        tea_weight REAL,
        rating INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tea_id) REFERENCES teas (id),
        FOREIGN KEY (teaware_id) REFERENCES teaware (id)
    )
    ''')
    # 注入一些默认数据
    cursor.execute("SELECT COUNT(*) FROM teas")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO teas (name, category, stock_grams, location) VALUES ('西湖 Dragon Well', '绿茶', 100.0, '冰箱')")
        cursor.execute("INSERT INTO teaware (name, material, capacity_ml) VALUES ('标准白瓷盖碗', '瓷', 130)")
    conn.commit()
    conn.close()
    print("✨ 茶仓数据库（tea_vault.db）已成功就位！")

if __name__ == '__main__':
    init_walnut_tea_db()