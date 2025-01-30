import mysql.connector
import environ
from pydantic import BaseModel

env = environ.Env()
environ.Env.read_env()

# Pydantic



# SQL
class Database:
    def __init__(self):
        self._conn = mysql.connector.connect(host=env('DB_HOST'), user=env("DB_USER"),
                    passwd=env("DB_PASSWORD"),database=env("DB_DATABASE"))
        self._cursor = self._conn.cursor()

    def cursor(self):
        self._conn.reconnect()
        return self._cursor
    
    def close(self):
        self._conn.close()

db = Database()

def items_search_via_name(text):
    db = mysql.connector.connect(host=env('DB_HOST'), user=env("DB_USER"),
                    passwd=env("DB_PASSWORD"),database=env("DB_DATABASE"))

    cursorObject = db.cursor()
    cursorObject.execute(f"""SELECT JSON_OBJECT("name", name, "mod", is_mods, "price", price) FROM items WHERE name LIKE '%{text}%' LIMIT 40""")
    result = cursorObject.fetchall()
    db.close()
    return result

def items_search_via_mod(text):
    db = mysql.connector.connect(host=env('DB_HOST'), user=env("DB_USER"),
                    passwd=env("DB_PASSWORD"),database=env("DB_DATABASE"))

    cursorObject = db.cursor()
    cursorObject.execute(f"""SELECT JSON_OBJECT("name", name, "mod", is_mods, "price", price) FROM items WHERE is_mods LIKE '%{text}%' LIMIT 40""")
    result = cursorObject.fetchall()
    db.close()
    return result
