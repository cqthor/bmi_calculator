import sqlite3


class DBHelper:
    def __init__(self, dbname="users.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.setup()

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, lang text)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_user(self, chat_id, lang):
        stmt = "INSERT INTO users (chat_id, lang) VALUES (?,?)"
        args = (chat_id, lang)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_user(self, chat_id):
        stmt = "SELECT * FROM users WHERE chat_id = (?)"
        args = (chat_id,)
        return self.conn.execute(stmt, args).fetchone()

    def get_lang(self, chat_id):
        stmt = "SELECT lang FROM users WHERE chat_id = (?)"
        args = (chat_id,)
        return self.conn.execute(stmt, args).fetchone()[0]

    def set_lang(self, chat_id, lang):
        stmt = "UPDATE users SET lang = (?) WHERE chat_id = (?)"
        args = (lang, chat_id)
        self.conn.execute(stmt, args)
        self.conn.commit()
