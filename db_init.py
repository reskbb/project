import sqlite3


def create_tables():
    create_table_users()
    create_table_tasks()


def create_table_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY);''')
    conn.commit()
    conn.close()


def create_table_tasks():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        name TEXT,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        deadline DATETIME,
        status TEXT,
        notified INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE);'''
                   )
    conn.commit()
    conn.close()
