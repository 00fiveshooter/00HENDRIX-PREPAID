import telebot
from config import BOT_TOKEN, ADMIN_ID
from utils import *

bot = telebot.TeleBot(BOT_TOKEN)
create_db()

def is_admin(user_id):
    return user_id == ADMIN_ID

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('💰 Deposit', '💼 My Balance')
    markup.row('💳 Buy Cards', '🎲 Feeling Lucky ($3.50)')
    markup.row('💯 Buy 100-Pack ($80)')
    markup.row('📦 My Orders')
    if is_admin(uid):
        markup.row('🛠 Admin Panel')
    bot.send_message(uid, "Welcome to the Prepaid Card Bot!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '💰 Deposit')
def deposit(message):
    bot.send_message(message.chat.id, "Send your BTC/LTC deposit manually, then send your TXID. Admin will add your balance.")

@bot.message_handler(func=lambda m: m.text == '💼 My Balance')
def balance(message):
    b = get_balance(message.from_user.id)
    bot.send_message(message.chat.id, f"💼 Your balance: ${b:.2f}")

@bot.message_handler(func=lambda m: m.text == '💳 Buy Cards')
def buy_card(message):
    cards = get_cards(card_type='normal')
    if not cards:
        return bot.send_message(message.chat.id, "No cards available.")
    msg = "💳 Cards Available:\n"
    for c in cards:
        msg += f"ID {c[0]} - ${c[4]:.2f} - /buy_{c[0]}\n"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text.startswith("/buy_"))
def handle_buy(message):
    uid = message.from_user.id
    card_id = int(message.text.split("_")[1])
    card = get_card_by_id(card_id)
    if not card or card[5] != 'normal':
        return bot.send_message(message.chat.id, "❌ Card not found.")
    if get_balance(uid) < card[4]:
        return bot.send_message(message.chat.id, "💸 Not enough balance.")
    deduct_balance(uid, card[4])
    remove_card(card_id)
    save_order(uid, *card[1:])
    bot.send_message(message.chat.id, f"✅ Your card:\n{card[1]}|{card[2]}|{card[3]}")

@bot.message_handler(func=lambda m: m.text == '🎲 Feeling Lucky ($3.50)')
def lucky(message):
    uid = message.from_user.id
    if get_balance(uid) < 3.5:
        return bot.send_message(message.chat.id, "💸 You need $3.50 to play.")
    card = get_random_card(card_type='lucky')
    if not card:
        return bot.send_message(message.chat.id, "⚠️ No stock.")
    deduct_balance(uid, 3.5)
    remove_card(card[0])
    save_order(uid, *card[1:])
    bot.send_message(message.chat.id, f"🎉 Lucky card:\n{card[1]}|{card[2]}|{card[3]}")

@bot.message_handler(func=lambda m: m.text == '💯 Buy 100-Pack ($80)')
def buy_pack(message):
    uid = message.from_user.id
    if get_balance(uid) < 80:
        return bot.send_message(message.chat.id, "💸 Not enough balance.")
    cards = get_multiple_cards(100, card_type='normal')
    if len(cards) < 100:
        return bot.send_message(message.chat.id, "❌ Not enough cards in stock.")
    deduct_balance(uid, 80)
    for card in cards:
        remove_card(card[0])
        save_order(uid, *card[1:])
    bot.send_message(uid, "🎉 Your 100-pack is ready!")
    for card in cards:
        bot.send_message(uid, f"{card[1]}|{card[2]}|{card[3]}")

@bot.message_handler(func=lambda m: m.text == '📦 My Orders')
def my_orders(message):
    orders = get_orders(message.from_user.id)
    if not orders:
        return bot.send_message(message.chat.id, "No orders yet.")
    msg = ""
    for o in orders:
        msg += f"{o[0]}|{o[1]}|{o[2]} - ${o[3]:.2f}\n"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == '🛠 Admin Panel')
def admin_menu(message):
    if not is_admin(message.from_user.id): return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('➕ Add Balance', '📤 Upload Card')
    markup.row('🍀 Upload Lucky Card', '💎 Upload High-End Card')
    markup.row('📊 View Stock', '🔙 Back')
    bot.send_message(message.chat.id, "👑 Admin Menu", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '➕ Add Balance')
def prompt_add_balance(message):
    bot.send_message(message.chat.id, "Use format:\n`addbalance user_id amount`")

@bot.message_handler(func=lambda m: m.text.startswith("addbalance"))
def do_add_balance(message):
    try:
        _, uid, amt = message.text.split()
        add_balance(int(uid), float(amt))
        bot.send_message(message.chat.id, f"✅ Balance added to {uid}")
    except:
        bot.send_message(message.chat.id, "❌ Format error.")

@bot.message_handler(func=lambda m: m.text == '📤 Upload Card')
def prompt_upload(message):
    bot.send_message(message.chat.id, "Send card like:\n`number|exp|cvv|price`")

@bot.message_handler(func=lambda m: m.text == '🍀 Upload Lucky Card')
def prompt_upload_lucky(message):
    bot.send_message(message.chat.id, "Send lucky card like:\n`number|exp|cvv`")

@bot.message_handler(func=lambda m: m.text == '💎 Upload High-End Card')
def prompt_upload_highend(message):
    bot.send_message(message.chat.id, "Send high-end card like:\n`number|exp|cvv|price`")

@bot.message_handler(func=lambda m: '|' in m.text and is_admin(m.from_user.id))
def upload_cards(message):
    try:
        parts = message.text.split('|')
        if len(parts) == 3:
            # Lucky card
            n, e, c = parts
            add_card(n.strip(), e.strip(), c.strip(), 0, card_type='lucky')
            bot.send_message(message.chat.id, "✅ Lucky card added.")
        elif len(parts) == 4:
            n, e, c, p = parts
            if message.reply_to_message and 'high' in message.reply_to_message.text.lower():
                add_card(n.strip(), e.strip(), c.strip(), float(p), card_type='high')
                bot.send_message(message.chat.id, "✅ High-end card added.")
            else:
                add_card(n.strip(), e.strip(), c.strip(), float(p), card_type='normal')
                bot.send_message(message.chat.id, "✅ Card added.")
        else:
            bot.send_message(message.chat.id, "❌ Invalid format.")
    except:
        bot.send_message(message.chat.id, "❌ Error adding card.")

@bot.message_handler(func=lambda m: m.text == '📊 View Stock')
def view_stock(message):
    normal = len(get_cards('normal'))
    lucky = len(get_cards('lucky'))
    high = len(get_cards('high'))
    msg = f"📦 Stock:\nNormal: {normal}\nLucky: {lucky}\nHigh-End: {high}"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text.startswith("/buy_high_"))
def buy_high_card(message):
    uid = message.from_user.id
    card_id = int(message.text.split("_")[2])
    card = get_card_by_id(card_id)
    if not card or card[5] != 'high':
        return bot.send_message(message.chat.id, "❌ High-end card not found.")
    if get_balance(uid) < card[4]:
        return bot.send_message(message.chat.id, "💸 Not enough balance.")
    deduct_balance(uid, card[4])
    remove_card(card_id)
    save_order(uid, *card[1:])
    bot.send_message(uid, f"💎 High-end card:\n{card[1]}|{card[2]}|{card[3]}")

bot.infinity_polling()
