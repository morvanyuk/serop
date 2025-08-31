import mysql.connector
import environ

env = environ.Env()
environ.Env.read_env()

db = mysql.connector.connect(
    host=env('DB_HOST'),
    user=env("DB_USER"),
    passwd=env("DB_PASSWORD"),
    database=env("DB_DATABASE")
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS servers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
""")

cursor.execute("""
ALTER TABLE items
ADD COLUMN server_id INT,
ADD FOREIGN KEY (server_id) REFERENCES servers(id);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id BIGINT UNSIGNED,
    ingredient_id BIGINT UNSIGNED,
    quantity INT,
    server_id INT,
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (ingredient_id) REFERENCES items(id),
    FOREIGN KEY (server_id) REFERENCES servers(id)
);
""")

db.commit()
db.close()

print("Database setup complete.")
