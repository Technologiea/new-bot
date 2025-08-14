import json
import os
import random
import time
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# Import and start keep_alive
from keep_alive import keep_alive
keep_alive()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is operational and ready"

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    click_id = request.args.get('click_id')
    event_id = request.args.get('status')
    date = request.args.get('payout')
    
    if click_id and event_id:
        try:
            user_id = str(click_id)
            load_users()
            if user_id not in users:
                users[user_id] = {'registered': False, 'deposited': False}
            
            event_lower = event_id.lower()
            if event_lower in ['reg', 'registration', 'reg_complete', 'register', 'signup', 'lead', 'ftd']:
                users[user_id]['registered'] = True
            elif event_lower in ['dep', 'deposit', 'first_deposit', 'payout'] and date:
                users[user_id]['deposited'] = True
            elif len(event_id) == 36 and '-' in event_id and date:
                users[user_id]['registered'] = True
            
            save_users()
        except Exception as e:
            print(f"Postback processing error: {e}")
    return 'OK', 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask).start()

# Configuration from environment variables
TOKEN = os.environ['TOKEN']
CHAT_ID = int(os.environ['CHAT_ID'])
AFF_LINK_BASE = os.environ['AFF_LINK_BASE']
PROMO_CODE = os.environ.get('PROMO_CODE', 'BETWIN190')
USERS_FILE = os.environ.get('USERS_FILE', 'users.json')

# Initialize bot
bot = telebot.TeleBot(TOKEN)
users = {}

# Image paths
IMAGE_PATH = '1.jpg'
REG_IMAGE_PATH = '2win.jpg'

def load_users():
    global users
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
                users = {str(k): v for k, v in users.items()}
    except Exception as e:
        print(f"User data load error: {e}")
        users = {}

def save_users():
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
    except Exception as e:
        print(f"User data save error: {e}")

def generate_crash_multiplier():
    return round(random.uniform(1.3, 4.0), 2) if random.random() > 0.8 else round(random.uniform(1.3, 2.5), 2)

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
        print(f"Feedback error: {e}")

# ============== CLEAN UI WITH INLINE KEYBOARDS ==============

def main_menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📌 REGISTER", callback_data="register"),
        InlineKeyboardButton("💰 DEPOSIT", callback_data="deposit"),
        InlineKeyboardButton("🎮 AVIATOR", callback_data="aviator"),
        InlineKeyboardButton("💎 MINES", callback_data="mines")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    user_id = str(user.id)
    load_users()
    
    if user_id not in users:
        users[user_id] = {'registered': False, 'deposited': False}
        save_users()
    
    welcome_msg = (
        f"🎉 Hello, @{user.username}!\n"
        "🌟 Welcome to <b>SureWin Signal Bot</b> — your smart path to winning big! 🚀\n\n"
        "We send real-time signals for <b>1win Aviator</b> & <b>Mines</b> — "
        "helping you play smarter and win more. 💸\n\n"
        "👥 Trusted by thousands\n"
        "🧠 Data-backed signals\n"
        "🛡️ Free after quick sign-up & deposit\n\n"
        "📲 Choose your next step below 👇"
    )
    
    with open(IMAGE_PATH, 'rb') as photo:
        bot.send_photo(
            message.chat.id, 
            photo, 
            caption=welcome_msg,
            parse_mode='HTML',
            reply_markup=main_menu_keyboard()
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = str(call.from_user.id)
    load_users()
    
    if call.data == "register":
        handle_register(call.message, user_id)
    elif call.data == "check_reg":
        check_registered(call.message, user_id)
    elif call.data == "deposit":
        handle_deposit(call.message, user_id)
    elif call.data == "check_dep":
        check_deposited(call.message, user_id)
    elif call.data == "aviator":
        aviator_signal(call.message, user_id)
    elif call.data == "mines":
        mines_signal(call.message, user_id)

def handle_register(message, user_id):
    reg_link = AFF_LINK_BASE + user_id
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎁 Register Now", url=reg_link),
        InlineKeyboardButton("✅ CHECK REGISTRATION", callback_data="check_reg")
    )
    
    reg_msg = (
        "📝 Let's get started!\n\n"
        f"🎁 Use promo code: <b>{PROMO_CODE}</b>\n"
        "❗️ If you see an old account, log out and click 'Register Now' again.\n\n"
        "⏳ After registering, tap '✅ CHECK REGISTRATION' below."
    )
    
    with open(REG_IMAGE_PATH, 'rb') as photo:
        bot.send_photo(
            message.chat.id, 
            photo, 
            caption=reg_msg,
            parse_mode='HTML',
            reply_markup=markup
        )

def check_registered(message, user_id):
    if users.get(user_id, {}).get('registered', False):
        success_msg = (
            "🎉 You've successfully registered! 🌟\n\n"
            "💰 Now, deposit to unlock full access & start winning!"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💰 DEPOSIT NOW", callback_data="deposit"))
        bot.send_message(
            message.chat.id, 
            success_msg, 
            parse_mode='HTML',
            reply_markup=markup
        )
    else:
        error_msg = (
            "❌ Registration not detected.\n\n"
            "✅ Please ensure you:\n"
            "1. Used the registration link\n"
            "2. Completed the sign-up\n"
            "3. Waited 2-3 minutes\n\n"
            "🔄 Then check again using the button below"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 CHECK AGAIN", callback_data="check_reg"))
        bot.send_message(
            message.chat.id, 
            error_msg, 
            parse_mode='HTML',
            reply_markup=markup
        )

def handle_deposit(message, user_id):
    if not users.get(user_id, {}).get('registered', False):
        bot.send_message(
            message.chat.id,
            "❌ You need to register first. 📌",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("📌 REGISTER NOW", callback_data="register")
            )
        )
        return
        
    dep_link = AFF_LINK_BASE + user_id
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("💸 Deposit Now", url=dep_link),
        InlineKeyboardButton("🔍 CHECK DEPOSIT", callback_data="check_dep")
    )
    
    dep_msg = (
        "💸 Ready to play? Deposit now to activate your account!\n\n"
        "🔹 Funds will be credited for play & wins.\n"
        "⏳ After depositing, tap '🔍 CHECK DEPOSIT' below."
    )
    
    bot.send_message(
        message.chat.id, 
        dep_msg, 
        parse_mode='HTML',
        reply_markup=markup
    )

def check_deposited(message, user_id):
    if not users.get(user_id, {}).get('registered', False):
        bot.send_message(
            message.chat.id,
            "❌ You need to register first. 📌",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("📌 REGISTER NOW", callback_data="register")
            )
        )
        return
        
    if users.get(user_id, {}).get('deposited', False):
        success_msg = "🎉 Deposit confirmed! 💸\nYou're all set to receive signals and start playing! 🎮"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🎮 AVIATOR SIGNALS", callback_data="aviator"),
            InlineKeyboardButton("💎 MINES SIGNALS", callback_data="mines")
        )
        bot.send_message(
            message.chat.id, 
            success_msg, 
            parse_mode='HTML',
            reply_markup=markup
        )
    else:
        error_msg = (
            "❌ Deposit not detected yet.\n\n"
            "⏳ Please wait 2-3 minutes after funding your account.\n"
            "Then check again using the button below"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 CHECK AGAIN", callback_data="check_dep"))
        bot.send_message(
            message.chat.id, 
            error_msg, 
            parse_mode='HTML',
            reply_markup=markup
        )

def aviator_signal(message, user_id):
    if not (users.get(user_id, {}).get('registered', False) and 
           users.get(user_id, {}).get('deposited', False)):
        bot.send_message(
            message.chat.id,
            "❌ Complete registration and deposit first!",
            reply_markup=InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton("📌 REGISTER", callback_data="register"),
                InlineKeyboardButton("💰 DEPOSIT", callback_data="deposit")
            )
        )
        return
        
    previous_multiplier = round(random.uniform(1.0, 1.87), 2)
    current_multiplier = generate_crash_multiplier()
    
    try:
        full_message = (
            "🚀 Aviator Signal Ready!\n\n"
            f"👉 Enter after {previous_multiplier}x\n"
            f"💰 Exit at {current_multiplier}x\n\n"
            "🛡️ Up to 2 protections\n"
            f"💸 Platform: [1win]({AFF_LINK_BASE}{user_id})"
        )
        bot.send_message(
            CHAT_ID, 
            full_message, 
            parse_mode='Markdown'
        )
        threading.Timer(180, send_feedback, args=(current_multiplier, 'aviator')).start()
        bot.send_message(
            message.chat.id,
            "✅ Signal sent to group! Check it now!"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Signal failed: {e}")

def mines_signal(message, user_id):
    if not (users.get(user_id, {}).get('registered', False) and 
           users.get(user_id, {}).get('deposited', False)):
        bot.send_message(
            message.chat.id,
            "❌ Complete registration and deposit first!",
            reply_markup=InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton("📌 REGISTER", callback_data="register"),
                InlineKeyboardButton("💰 DEPOSIT", callback_data="deposit")
            )
        )
        return
        
    num_mines, pos_str, multiplier = generate_mines_signal()
    
    try:
        full_message = (
            "💎 Mines Signal Ready!\n\n"
            f"Set Mines: {num_mines}\n"
            f"Click Sequence: {pos_str}\n"
            f"💰 Cash out at {multiplier}x\n\n"
            "🛡️ Up to 2 protections\n"
            f"💸 Platform: [1win]({AFF_LINK_BASE}{user_id})"
        )
        bot.send_message(
            CHAT_ID, 
            full_message, 
            parse_mode='Markdown'
        )
        threading.Timer(150, send_feedback, args=(multiplier, 'mines')).start()
        bot.send_message(
            message.chat.id,
            "✅ Signal sent to group! Check it now!"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Signal failed: {e}")

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    user_id = str(message.from_user.id)
    load_users()
    
    if not users.get(user_id, {}).get('registered', False):
        bot.send_message(
            message.chat.id,
            "📌 Please register first to get started 👇",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("📌 REGISTER NOW", callback_data="register")
            )
        )
    elif not users.get(user_id, {}).get('deposited', False):
        bot.send_message(
            message.chat.id,
            "💰 You're registered, but haven't deposited yet. Deposit now to unlock signals! 👇",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("💰 DEPOSIT NOW", callback_data="deposit")
            )
        )
    else:
        bot.send_message(
            message.chat.id,
            "🎮 You're all set! Choose a game to get your next signal! 👇",
            reply_markup=InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton("🎮 AVIATOR", callback_data="aviator"),
                InlineKeyboardButton("💎 MINES", callback_data="mines")
            )
        )

bot.polling()
