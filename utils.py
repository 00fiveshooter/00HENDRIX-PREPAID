commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row:
        return row[0]
    else:
        c.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
        conn.commit()
        return 0

def add_balance(user_id, amount):
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def deduct_balance(user_id, amount):
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def add_card(number, exp, cvv, price):
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()
    c.execute("INSERT INTO cards (number, exp, cvv, price) VALUES (?, ?, ?, ?)", (number, exp, cvv, price))
    conn.commit()
    conn.close()

def get_cards():
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()
    c.execute("SELECT id, number, exp, cvv, price FROM cards")
    rows = c.fetchall()
    conn.close()
    return rows

def get_card_by_id(card_id):
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
    row = c.fetchone()
    conn.close()
    return row

def remove_card(card_id):
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()
    c.execute("DELETE FROM cards WHERE id = ?", (card_id,))
    conn.commit()
    conn.close()

def get_random_card():
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()
    c.execute("SELECT * FROM cards ORDER BY RANDOM() LIMIT 1")
    card = c.fetchone()
    conn.close()
    return card

def save_order(user_id, number, exp, cvv, price):
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_id, card_number, card_exp, card_cvv, price) VALUES (?, ?, ?, ?, ?)",
              (user_id, number, exp, cvv, price))
    conn.commit()
    conn.close()

def get_orders(user_id):
    conn = sqlite3.connect('cards.db')
    c = conn.cursor()
    c.execute("SELECT card_number, card_exp, card_cvv, price FROM orders WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows
