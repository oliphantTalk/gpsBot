import sqlite3
import re

class InMemDb:

    db = sqlite3.connect("file::memory:", check_same_thread=False)
    user_table = "GPS_USERS"

    # Se inicializa la base de datos con algunos usuarios predefinidos.
    def __init__(self):
        cur = self.db.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS {self.user_table} (CHAT_ID INTEGER PRIMARY KEY , username text, role text, points INTEGER)")
        self.add_admin()
        self.db.commit()


    def basic(self, username):
        try:
            cur = self.db.cursor()
            query = "SELECT username, role FROM DSA_USERS WHERE username = ?"
            """resultado = []
                for q in query.split(";"):
                if re.search('INSERT INTO DSA_USERS VALUES', q, re.IGNORECASE):
                    resultado.append(tuple(("fake_flag", "pinta drop?")))
                    return resultado
                if re.search('DROP TABLE DSA_USERS', q, re.IGNORECASE):
                    resultado.append(tuple(("real_flag", "ahora si bby mandale log")))
                    return resultado"""
            return cur.execute(query, username).fetchall()
        except:
            return []

    def add_admin(self):
        try:
            cur = self.db.cursor()
            cur.execute(f"INSERT INTO {self.user_table} VALUES (123456, 'admin', 'admin', 0)")
            self.db.commit()
        except:
            print("Error agrega admin")
            pass

    def user_exists(self, chat_id):
        try:
            cur = self.db.cursor()
            return cur.execute(f"SELECT * FROM {self.user_table} WHERE CHAT_ID = ?", (chat_id,)).fetchall()
        except:
            print("Error user exists")
            return None

    def new_user(self, chat_id, username):
        try:
            cur = self.db.cursor()
            cur.execute(f"INSERT INTO {self.user_table} VALUES ('{chat_id}', '{username}', 'user', 0)")
            self.db.commit()
        except:
            print("Error user exists")
            return None


    def add_points(self, chat_id, points):
        try:
            cur = self.db.cursor()
            actual_points = cur.execute(f"SELECT points FROM {self.user_table} WHERE CHAT_ID = ?", (chat_id,)).fetchone()
            cur.execute(f"UPDATE {self.user_table} SET points = {actual_points + points} WHERE CHAT_ID = ?", (chat_id, ))
            self.db.commit()
        except:
            print("Error user exists")
            return None