import json
import os
import random
import time
import threading
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
from keep_alive import keep_alive

# Start keep_alive server
keep_alive()

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive"

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    click_id = request.args.get('click_id')
    event_id = request.args.get('status')
    date = request.args.get('payout')
    print(f"DEBUG: Postback received at {time.strftime('%H:%M:%S')}: click_id={click_id}, event_id={event_id}, date={date}")
    
    if click_id and event_id:
        try:
            user_id = str(click_id)
            load_users()
            if user_id not in users:
                users[user_id] = {'registered': False, 'deposited': False}
            
            event_lower = event_id.lower()
            if event_lower in ['reg', 'registration', 'reg_complete', 'register', 'signup', 'lead']:
                users[user_id]['registered'] = True
                print(f"DEBUG: User {user_id} marked as registered")
            elif event_lower in ['dep', 'deposit', 'first_deposit', 'payout'] and date:
                users[user_id]['deposited'] = True
                print(f"DEBUG: User {user_id} marked as deposited")
            elif len(event_id) == 36 and '-' in event_id and date:
                users[user_id]['registered'] = True
                print(f"DEBUG: User {user_id} marked as registered (UUID)")
            else:
                print(f"DEBUG: Unknown event_id {event_id}")
            
            save_users()
        except Exception as e:
            print(f"DEBUG: Postback error: {e}")
    else:
        print(f"DEBUG: Missing parameters")
    return 'OK', 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask).start()

# Environment variables / config
TOKEN = os.environ.get('TOKEN', 'BOT_TOKEN_HERE')
bot = telebot.TeleBot(TOKEN)
CHAT_ID = int(os.environ.get('CHAT_ID', '-1002889312280'))
AFF_LINK_BASE = os.environ.get('AFF_LINK_BASE', 'https://1wvlau.life/?open=register&p=koqg&sub1=')
IMAGE_PATH = '1.jpg'
REG_IMAGE_PATH = '2win.jpg'
PROMO_CODE = os.environ.get('PROMO_CODE', 'BETWIN190')
USERS_FILE = os.environ.get('USERS_FILE', 'users.json')
users = {}

# Utility functions
def load_users():
    global users
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users = {str(k): v for k, v in json.load(f).items()}
        else:
            users = {}
    except Exception as e:
        print(f"DEBUG: Error loading users: {e}")
        users = {}

def save_users():
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
    except Exception as e:
        print(f"DEBUG: Error saving users: {e}")

def generate_crash_multiplier():
    return round(random.uniform(1.3, 2.5), 2) if random.random() <= 0.8 else round(random.uniform(2.5, 4.0), 2)

def generate_mines_signal():
    num_mines = random.randint(1, 5)
    num_clicks = random.randint(3, 8)
    positions = random.sample(range(1, 26), num_clicks)
    pos_str = ', '.join([f"({(p-1)//5 + 1}, {(p-1)%5 + 1})" for p in positions])
    multiplier = round(1.0 + num_clicks * 0.3 + random.uniform(0, 1), 2)
    return num_mines, pos_str, multiplier

def send_feedback(multiplier, game):
    try:
        bot.send_message(CHAT_ID, f"✅ GREEN ({multiplier}x)")
    except Exception as e:
        print(f"DEBUG: Error sending feedback: {e}")

# Handlers
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    load_users()
    if user_id not in users:
        users[user_id] = {'registered': False, 'deposited': False}
        save_users()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('📌 REGISTER')
    with open(IMAGE_PATH, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f"🎉 Hello, @{message.from_user.username}! 🚀 Welcome to SureWin Bot!", parse_mode='HTML')
    bot.send_message(message.chat.id, "Start your winning journey! 🎯", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '📌 REGISTER')
def handle_register(message):
    user_id = str(message.from_user.id)
    reg_link = AFF_LINK_BASE + user_id
    inline_markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🎁 Register Now", url=reg_link))
    with open(REG_IMAGE_PATH, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f"📝 Use promo code: <b>{PROMO_CODE}</b>", parse_mode='HTML', reply_markup=inline_markup)
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('✅ CHECK REGISTRATION')
    bot.send_message(message.chat.id, "Ready? Check your status!", reply_markup=reply_markup)

@bot.message_handler(func=lambda m: m.text == '✅ CHECK REGISTRATION')
def check_registered(message):
    user_id = str(message.from_user.id)
    load_users()
    if users.get(user_id, {}).get('registered', False):
        bot.send_message(message.chat.id, "🎉 Registration complete! Deposit next!")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('💰 DEPOSIT')
    else:
        bot.send_message(message.chat.id, "❌ Registration pending!")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('✅ CHECK REGISTRATION')
    bot.send_message(message.chat.id, "Proceed ⬇️", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '💰 DEPOSIT')
def handle_deposit(message):
    user_id = str(message.from_user.id)
    dep_link = AFF_LINK_BASE + user_id
    inline_markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🌐 Deposit Now", url=dep_link))
    bot.send_message(message.chat.id, "💰 Top-up and click check deposit!", reply_markup=inline_markup)
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('🔍 CHECK DEPOSIT')
    bot.send_message(message.chat.id, "Fund your account! 🚀", reply_markup=reply_markup)

@bot.message_handler(func=lambda m: m.text == '🔍 CHECK DEPOSIT')
def check_deposited(message):
    user_id = str(message.from_user.id)
    load_users()
    if not users.get(user_id, {}).get('registered', False):
        bot.send_message(message.chat.id, "❌ Register first!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('📌 REGISTER'))
    elif users.get(user_id, {}).get('deposited', False):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row('🎮 AVIATOR SIGNALS', '💎 MINES SIGNALS')
        bot.send_message(message.chat.id, "🎉 Deposit confirmed!", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Deposit pending!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('🔍 CHECK DEPOSIT'))

@bot.message_handler(func=lambda m: m.text == '🎮 AVIATOR SIGNALS')
def aviator_signal(message):
    user_id = str(message.from_user.id)
    load_users()
    if not (users.get(user_id, {}).get('registered') and users.get(user_id, {}).get('deposited')):
        bot.send_message(message.chat.id, "❌ Complete registration & deposit first!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('📌 REGISTER', '💰 DEPOSIT'))
        return
    prev_mult = round(random.uniform(1.0, 1.87), 2)
    curr_mult = generate_crash_multiplier()
    caption = f"🎯 Aviator Signal\nEnter after {prev_mult}x\nExit at {curr_mult}x"
    with open(IMAGE_PATH, 'rb') as photo:
        bot.send_photo(CHAT_ID, photo, caption=caption)
    threading.Timer(180, send_feedback, args=(curr_mult, 'aviator')).start()
    bot.send_message(message.chat.id, "Signal sent to group! 🎉")

@bot.message_handler(func=lambda m: m.text == '💎 MINES SIGNALS')
def mines_signal(message):
    user_id = str(message.from_user.id)
    load_users()
    if not (users.get(user_id, {}).get('registered') and users.get(user_id, {}).get('deposited')):
        bot.send_message(message.chat.id, "❌ Complete registration & deposit first!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('📌 REGISTER', '💰 DEPOSIT'))
        return
    num_mines, pos_str, mult = generate_mines_signal()
    caption = f"🎯 Mines Signal\nSet Mines: {num_mines}\nClicks: {pos_str}\nCashout at {mult}x"
    with open(IMAGE_PATH, 'rb') as photo:
        bot.send_photo(CHAT_ID, photo, caption=caption)
    threading.Timer(150, send_feedback, args=(mult, 'mines')).start()
    bot.send_message(message.chat.id, "Signal sent to group! 🎉")

# Default fallback
@bot.message_handler(func=lambda m: True)
def fallback(message):
    user_id = str(message.from_user.id)
    load_users()
    status = users.get(user_id, {'registered': False, 'deposited': False})
    if not status['registered']:
        bot.send_message(message.chat.id, "📌 Register to start!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('📌 REGISTER'))
    elif not status['deposited']:
        bot.send_message(message.chat.id, "💰 Deposit to continue!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('💰 DEPOSIT'))
    else:
        bot.send_message(message.chat.id, "🎮 Choose your game!", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row('🎮 AVIATOR SIGNALS', '💎 MINES SIGNALS'))

bot.polling()
