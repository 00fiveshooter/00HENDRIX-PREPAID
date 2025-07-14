import sqlite3

DB_NAME = 'cards.db'

def create_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT,
        exp TEXT,
        cvv TEXT,
        price REAL,
        type TEXT DEFAULT 'normal'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        user_id INTEGER,
        number TEXT,
        exp TEXT,
        cvv TEXT,
        price REAL
    )''')

    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0.0

def add_balance(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def deduct_balance(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def add_card(number, exp, cvv, price, card_type='normal'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO cards (number, exp, cvv, price, type) VALUES (?, ?, ?, ?, ?)",
              (number, exp, cvv, price, card_type))
    conn.commit()
    conn.close()

def get_cards(card_type='normal'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE type=?", (card_type,))
    result = c.fetchall()
    conn.close()
    return result

def get_card_by_id(card_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE id=?", (card_id,))
    result = c.fetchone()
    conn.close()
    return result

def get_random_card(card_type='lucky'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE type=? ORDER BY RANDOM() LIMIT 1", (card_type,))
    result = c.fetchone()
    conn.close()
    return result

def get_multiple_cards(count, card_type='normal'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE type=? LIMIT ?", (card_type, count))
    result = c.fetchall()
    conn.close()
    return result

def remove_card(card_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM cards WHERE id=?", (card_id,))
    conn.commit()
    conn.close()

def save_order(user_id, number, exp, cvv, price):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_id, number, exp, cvv, price) VALUES (?, ?, ?, ?, ?)",
              (user_id, number, exp, cvv, price))
    conn.commit()
    conn.close()

def get_orders(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT number, exp, cvv, price FROM orders WHERE user_id=?", (user_id,))
    result = c.fetchall()
    conn.close()
    return result

