import mysql.connector
import environ
from pydantic import BaseModel

env = environ.Env()
environ.Env.read_env()

# Pydantic

# SQL
class Database:
    def __init__(self):
        self._conn = mysql.connector.connect(
            host=env('DB_HOST'),
            user=env("DB_USER"),
            passwd=env("DB_PASSWORD"),
            database=env("DB_DATABASE")
        )
        self._cursor = self._conn.cursor()

    def get_cursor(self):
        self._conn.reconnect()
        return self._conn.cursor(dictionary=True)

    def execute(self, query, params=None):
        cursor = self.get_cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_one(self, query, params=None):
        cursor = self.get_cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def commit(self, query, params=None):
        cursor = self.get_cursor()
        cursor.execute(query, params)
        self._conn.commit()
        cursor.close()

    def close(self):
        self._conn.close()

db = Database()

def items_search_via_name(text, server_id):
    query = """
        SELECT id, name, is_mods, price
        FROM items
        WHERE name LIKE %s AND server_id = %s
        LIMIT 40
    """
    return db.execute(query, (f"%{text}%", server_id))

def items_search_via_mod(text, server_id):
    query = """
        SELECT id, name, is_mods, price
        FROM items
        WHERE is_mods LIKE %s AND server_id = %s
        LIMIT 40
    """
    return db.execute(query, (f"%{text}%", server_id))

def get_servers():
    query = "SELECT * FROM servers"
    return db.execute(query)

def add_server(name):
    query = "INSERT INTO servers (name) VALUES (%s)"
    db.commit(query, (name,))

def add_item(name, is_mods, price, server_id):
    query = "INSERT INTO items (name, is_mods, price, server_id) VALUES (%s, %s, %s, %s)"
    db.commit(query, (name, is_mods, price, server_id))

def get_recipe(item_id, server_id):
    query = """
        SELECT ingredient_id, quantity
        FROM recipes
        WHERE item_id = %s AND server_id = %s
    """
    return db.execute(query, (item_id, server_id))

def get_item_price(item_id, server_id):
    query = "SELECT price FROM items WHERE id = %s AND server_id = %s"
    result = db.execute_one(query, (item_id, server_id))
    return result['price'] if result else None

def add_recipe(item_id, ingredient_id, quantity, server_id):
    query = "INSERT INTO recipes (item_id, ingredient_id, quantity, server_id) VALUES (%s, %s, %s, %s)"
    db.commit(query, (item_id, ingredient_id, quantity, server_id))
