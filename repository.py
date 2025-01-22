import sqlite3

class Repository:
    def __init__(self,db_name='database.db'):
        self.db_name = db_name


    def create_user(self,user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''INSERT OR IGNORE INTO users (id) VALUES (?);''', (user_id,))
        conn.commit()
        conn.close()
    def status_change(self,user_id,name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE tasks SET status = 'YES' WHERE user_id = ? AND name = ?''',(user_id,name))
        conn.commit()
        conn.close()


    def create_task(self, user_id, name, desc, created_at, deadl):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO tasks(user_id,name,description, created_at, deadline,status,notified) VALUES (?,?,?,?,?,'NO',0);''',
            (user_id, name, desc, created_at, deadl))
        conn.commit()
        conn.close()


    def delete_user(self,user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM users WHERE id = ?;''', (user_id,))
        conn.commit()
        conn.close()


    def delete_task(self,name,user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM tasks WHERE name = ? AND user_id = ?;''', (name,user_id))
        conn.commit()
        conn.close()


    def get_tasks_by_user_id(self,user_id, limit, offset):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT name FROM tasks WHERE status = 'NO' AND user_id = ? LIMIT  ? OFFSET  ? ;''', (user_id, limit, offset))
        tasks_of_user = cursor.fetchall()
        conn.close()
        return tasks_of_user

    def get_by_name(self,name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''SELECT description,deadline FROM tasks WHERE name = ? ;''', (name,))
        desc_of_user = cursor.fetchall()
        conn.close()
        return desc_of_user


    def update_task_status(self,task, user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''UPDATE tasks SET name = ? WHERE user_id = ? AND name = ?;''', (task, user_id))
        conn.commit()
        conn.close()
