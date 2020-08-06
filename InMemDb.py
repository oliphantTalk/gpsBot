import sqlite3
import re

class InMemDb:

    db = sqlite3.connect("file::memory:", check_same_thread=False)
    user_table = "GPS_USERS"
    users_reports = "USERS_REPORTS"
    report_id_by_user = {}

    def __init__(self):
        cur = self.db.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS {self.user_table} (CHAT_ID INTEGER PRIMARY KEY , username text, role text, gender text, bio text,  points INTEGER)")
        cur.execute(f"CREATE TABLE IF NOT EXISTS {self.users_reports} (REPORT_ID INTEGER PRIMARY KEY, USER_ID INTEGER, "
                    f"photo text, location_lat text, location_long text, description text)")
        self.add_admin()
        self.db.commit()


    def add_admin(self):
        try:
            cur = self.db.cursor()
            cur.execute(f"INSERT INTO {self.user_table} VALUES (-123123123, 'admin', 'admin', 'male', 'a super admin', 0)")
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
            cur.execute(f"INSERT INTO {self.user_table} VALUES ('{chat_id}', '{username}', '', 'user', '', 0)")

            self.db.commit()
        except:
            print("Error new user")
            return None


    def add_points(self, chat_id, points):
        try:
            cur = self.db.cursor()
            actual_points = cur.execute(f"SELECT points FROM {self.user_table} WHERE CHAT_ID = ?", (chat_id,)).fetchone()[0]
            cur.execute(f"UPDATE {self.user_table} SET points = {actual_points + points} WHERE CHAT_ID = ?", (chat_id, ))
            self.db.commit()
        except:
            print("Error add points")
            return None

    def add_user_report_location(self, chat_id, location_lat, location_long):
        try:
            cur = self.db.cursor()
            cur.execute(f"UPDATE {self.users_reports} SET location_lat = '{location_lat}', location_long = '{location_long}' "
                        f"WHERE REPORT_ID = ?", (self.report_id_by_user[chat_id],))
            self.db.commit()
        except:
            print("Error update location")
            return None


    def new_report_w_pic(self, chat_id, photo_name):
        try:
            r_id = self.get_new_report_id(chat_id)
            cur = self.db.cursor()
            cur.execute(f"INSERT INTO {self.users_reports} "
                        f"VALUES ('{r_id}', "
                        f"'{chat_id}', "
                        f"'{photo_name}', '', '', ''"
                        f")")
            self.db.commit()
            return r_id
        except:
            print("Error new pic")
            return None

    def last_reports(self):
        try:
            cur = self.db.cursor()
            return cur.execute(f"SELECT * FROM {self.users_reports} ORDER BY REPORT_ID").fetchall()
        except:
            print("Error last report")
            return None


    def add_user_report_description(self, chat_id, desc):
        try:
            cur = self.db.cursor()
            cur.execute(f"UPDATE {self.users_reports} SET description = '{desc}' WHERE REPORT_ID = ?", (self.report_id_by_user[chat_id],))
            self.db.commit()
        except:
            print("Error add report description")
            return None

    def update_bio(self, chat_id, bio_val):
        try:
            cur = self.db.cursor()
            cur.execute(f"UPDATE {self.user_table} SET bio = '{bio_val}' WHERE CHAT_ID = ?", (chat_id,))
            self.db.commit()
        except:
            print("Error update bio")
            return None

    def update_gender(self, chat_id, gender_val):
        try:
            cur = self.db.cursor()
            cur.execute(f"UPDATE {self.user_table} SET gender = '{gender_val}' WHERE CHAT_ID = ?", (chat_id,))
            self.db.commit()
        except:
            print("Error update gender")
            return None

    def user_points(self, chat_id):
        try:
            cur = self.db.cursor()
            return cur.execute(f"SELECT points FROM {self.user_table} WHERE CHAT_ID = ?", (chat_id,)).fetchone()
        except:
            print("Error user points")
            return None

    def get_new_report_id(self, chat_id):
        if self.report_id_by_user.get(chat_id):
            self.update_report_id(chat_id)
        else:
            self.report_id_by_user[chat_id] = 1
        return self.report_id_by_user.get(chat_id)

    def update_report_id(self, chat_id):
        self.report_id_by_user[chat_id] = self.report_id_by_user.get(chat_id) + 1