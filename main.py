import json
import os
import random
import time
import threading
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive  # Ensure this file exists or replace with appropriate keep-alive logic

# Start keep_alive server (for Replit or similar hosting)
keep_alive()

app = Flask(__name__)

# Global users dict and config
USERS_FILE = os.environ.get('USERS_FILE', 'users.json')
TOKEN = os.environ.get('TOKEN', '7774262573:AAFmsQ9OMnvtty0jNVGR3S7jixrRuSkKPqk')  # Replace with your bot token or set env var
CHAT_ID = int(os.environ.get('CHAT_ID', '-1002889312280'))  # Your group/channel chat ID
AFF_LINK_BASE = os.environ.get('AFF_LINK_BASE', 'https://1wvlau.life/?open=register&p=koqg&sub1=')
PROMO_CODE = os.environ.get('PROMO_CODE', 'BETWIN190')
IMAGE_PATH = '1.jpg'
REG_IMAGE_PATH = '2win.jpg'

users = {}
bot = telebot.TeleBot(TOKEN)

def load_users():
    global users
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
                users = {str(k): v for k, v in users.items()}
        else:
            users = {}
        print(f"DEBUG: Loaded users at {time.strftime('%H:%M:%S')}: {users}")
    except Exception as e:
        print(f"DEBUG: Error loading users file: {e}")
        users = {}

def save_users():
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        print(f"DEBUG: Saved users at {time.strftime('%H:%M:%S')}: {users}")
    except Exception as e:
        print(f"DEBUG: Error saving users file: {e}")

@app.route('/')
def home():
    return "I'm alive"

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    click_id = request.args.get('click_id')
    event_id = request.args.get('status')
    payout = request.args.get('payout')
    print(f"DEBUG: Postback received at {time.strftime('%H:%M:%S')}: click_id={click_id}, status={event_id}, payout={payout}")

    if click_id and event_id:
        user_id = str(click_id)
        load_users()
        if user_id not in users:
            users[user_id] = {'registered': False, 'deposited': False}

        event_lower = event_id.lower()
        if event_lower in ['reg', 'registration', 'reg_complete', 'register', 'signup', 'lead', 'ftd']:
            users[user_id]['registered'] = True
            print(f"DEBUG: User {user_id} marked as registered")
        elif event_lower in ['dep', 'deposit', 'first_deposit', 'payout'] and payout:
            users[user_id]['deposited'] = True
            print(f"DEBUG: User {user_id} marked as deposited")
        elif len(event_id) == 36 and '-' in event_id and payout:
            users[user_id]['registered'] = True
            print(f"DEBUG: User {user_id} marked as registered (UUID)")
        else:
            print(f"DEBUG: Unknown event_id {event_id}")

        save_users()
    else:
        print("DEBUG: Missing click_id or status in postback")

    return 'OK', 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Start Flask server in a daemon thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Utilities to generate signals
def generate_crash_multiplier():
    if random.random() <= 0.8:
        return round(random.uniform(1.3, 2.5), 2)
    return round(random.uniform(2.5, 4.0), 2)

def generate_mines_signal():
    num_mines = random.randint(1, 5)
    num_clicks = random.randint(3, 8)
    positions = random.sample(range(1, 26), num_clicks)
    pos_str = ', '.join([f"({(p-1)//5 + 1}, {(p-1)%5 + 1})" for p in positions])
    multiplier = round(1.0 + num_clicks * 0.3 + random.uniform(0, 1), 2)
    return num_mines, pos_str, multiplier

def send_feedback(multiplier, game):
    try:
        message = f"✅ GREEN ({multiplier}x)" if game in ['aviator', 'mines'] else f"✅ GREEN ({multiplier}x)"
        bot.send_message(CHAT_ID, message)
    except Exception as e:
        print(f"DEBUG: Error sending feedback: {e}")

# Telegram command handlers
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    load_users()
    if user_id not in users:
        users[user_id] = {'registered': False, 'deposited': False}
        save_users()

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📌 Register", url=AFF_LINK_BASE + user_id))
    with open(IMAGE_PATH, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f"🎉 Hello, @{message.from_user.username}!  \n🌟 Welcome to <b>SureWin Signal Bot</b> — your smart path to winning big! 🚀  \nWe send real-time signals for <b>1win Aviator</b> & <b>Mines</b> — helping you play smarter and win more. 💸  \n👥 Trusted by thousands  \n🧠 Data-backed signals  \n🛡️ Free after quick sign-up & deposit  \n📲 Tap below to start your journey and unlock premium signals! 🌈", parse_mode='HTML', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '📌 Register' or m.text == '📌 REGISTER')
def handle_register(message):
    user_id = str(message.from_user.id)
    reg_link = AFF_LINK_BASE + user_id
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎁 Register Now", url=reg_link))
    with open(REG_IMAGE_PATH, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f"📝 Let's get started!  \n🎁 Use promo code: <b>{PROMO_CODE}</b>  \n❗️ If you see an old account, logout and click 'Register Now' again.  \n⏳ After registering, tap '✅ CHECK REGISTRATION'.", parse_mode='HTML', reply_markup=markup)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Check Registration", url=reg_link))
    bot.send_message(message.chat.id, "Ready to win? 🚀  \nTap below to check your registration status 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '✅ Check Registration' or m.text == '✅ CHECK REGISTRATION')
def check_registered(message):
    user_id = str(message.from_user.id)
    load_users()
    reg_link = AFF_LINK_BASE + user_id
    if users.get(user_id, {}).get('registered', False):
        bot.send_message(message.chat.id, "🎉 You’ve successfully registered! 🌟  \n💰 Now, deposit to unlock full access & start winning!")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💰 Deposit", url=reg_link))
        bot.send_message(message.chat.id, "Next step! Tap below 👇", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Registration not detected.  \n✅ Please ensure you:  \n1. Used the registration link  \n2. Completed the sign-up  \n3. Waited 2-3 minutes  \n🔄 Then, tap '✅ CHECK REGISTRATION' again.")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Check Registration", url=reg_link))
        bot.send_message(message.chat.id, "Try again! Tap below 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '💰 Deposit' or m.text == '💰 DEPOSIT')
def handle_deposit(message):
    user_id = str(message.from_user.id)
    dep_link = AFF_LINK_BASE + user_id
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🌐 Deposit Now", url=dep_link))
    bot.send_message(message.chat.id, "💸 Ready to play? Deposit now to activate your account!  \n🔹 Funds will be credited for play & wins.  \n⏳ After depositing, tap '🔍 CHECK DEPOSIT'!")
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔍 Check Deposit", url=dep_link))
    bot.send_message(message.chat.id, "Fund your account! Tap below 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '🔍 Check Deposit' or m.text == '🔍 CHECK DEPOSIT')
def check_deposited(message):
    user_id = str(message.from_user.id)
    load_users()
    dep_link = AFF_LINK_BASE + user_id
    if not users.get(user_id, {}).get('registered', False):
        bot.send_message(message.chat.id, "❌ You need to register first. 📌  \nTap below to get started 👇")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📌 Register", url=dep_link))
        bot.send_message(message.chat.id, "Start here! Tap below 👇", reply_markup=markup)
    elif users.get(user_id, {}).get('deposited', False):
        bot.send_message(message.chat.id, "🎉 Deposit confirmed! 💸  \nYou're all set to receive signals and start playing! 🎮")
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("🎮 Aviator Signals", callback_data='aviator'),
                   InlineKeyboardButton("💎 Mines Signals", callback_data='mines'))
        bot.send_message(message.chat.id, "Choose your game below 👇", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Deposit not detected yet.  \n⏳ Please wait 2-3 minutes after funding your account.  \nThen tap '🔍 CHECK DEPOSIT' again.")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔍 Check Deposit", url=dep_link))
        bot.send_message(message.chat.id, "Check again! Tap below 👇", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '🎮 Aviator Signals' or m.text == '🎮 AVIATOR SIGNALS')
def aviator_signal(message):
    user_id = str(message.from_user.id)
    load_users()
    if not (users.get(user_id, {}).get('registered', False) and users.get(user_id, {}).get('deposited', False)):
        bot.send_message(message.chat.id, "❓ Not sure what that means. Click to /start")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📌 Register", url=AFF_LINK_BASE + user_id))
        bot.send_message(message.chat.id, "📌 Please register first to get started 👇", reply_markup=markup)
        return
    previous_multiplier = round(random.uniform(1.0, 1.87), 2)
    current_multiplier = generate_crash_multiplier()
    full_message = (
        "🎯 Aviator Signal Ready! 🎮  \n"
        f"📱 Play: <a href='https://1wvlau.life/?open=register&p=koqg'>Here</a>  \n"
        f"👉 Enter after {previous_multiplier}x  \n"
        f"💰 Exit at {current_multiplier}x  \n"
        "🛡️ Up to 2 protections  \n"
        f"💸 Platform: <a href='https://1wvlau.life/?open=register&p=koqg'>Here</a>"
    )
    try:
        print(f"DEBUG: Sending Aviator signal to CHAT_ID {CHAT_ID}")
        with open(IMAGE_PATH, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo, caption=full_message, parse_mode='HTML')
        threading.Timer(180, send_feedback, args=(current_multiplier, 'aviator')).start()
        bot.send_message(message.chat.id, "Signal sent! 🎉 Check it! 🚀")
    except Exception as e:
        print(f"DEBUG: Error sending Aviator signal: {e}")
        bot.send_message(message.chat.id, f"❌ Signal failed: {e}")

@bot.message_handler(func=lambda m: m.text == '💎 Mines Signals' or m.text == '💎 MINES SIGNALS')
def mines_signal(message):
    user_id = str(message.from_user.id)
    load_users()
    if not (users.get(user_id, {}).get('registered', False) and users.get(user_id, {}).get('deposited', False)):
        bot.send_message(message.chat.id, "❓ Not sure what that means. Click to /start")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📌 Register", url=AFF_LINK_BASE + user_id))
        bot.send_message(message.chat.id, "📌 Please register first to get started 👇", reply_markup=markup)
        return
    num_mines, pos_str, multiplier = generate_mines_signal()
    full_message = (
        "🎯 Mines Signal Ready! 💎  \n"
        f"📱 Play: <a href='https://1wvlau.life/?open=register&p=koqg'>Here</a>  \n"
        f"Set Mines: {num_mines}  \n"
        f"Click Sequence: {pos_str}  \n"
        f"💰 Cash out at {multiplier}x  \n"
        "🛡️ Up to 2 protections  \n"
        f"💸 Platform: <a href='https://1wvlau.life/?open=register&p=koqg'>Here</a>"
    )
    try:
        print(f"DEBUG: Sending Mines signal to CHAT_ID {CHAT_ID}")
        with open(IMAGE_PATH, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo, caption=full_message, parse_mode='HTML')
        threading.Timer(150, send_feedback, args=(multiplier, 'mines')).start()
        bot.send_message(message.chat.id, "Signal sent! 🎉 Check it! 🚀")
    except Exception as e:
        print(f"DEBUG: Error sending Mines signal: {e}")
        bot.send_message(message.chat.id, f"❌ Signal failed: {e}")

@bot.message_handler(func=lambda message: True)
def handle_random_message(message):
    user_id = str(message.from_user.id)
    load_users()
    status = users.get(user_id, {'registered': False, 'deposited': False})
    
    if not status.get('registered', False):
        bot.send_message(message.chat.id, "❓ Not sure what that means. Click to /start")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📌 Register", url=AFF_LINK_BASE + user_id))
        bot.send_message(message.chat.id, "📌 Please register first to get started 👇", reply_markup=markup)
    elif not status.get('deposited', False):
        bot.send_message(message.chat.id, "❓ You’re registered, but haven’t deposited yet.  \n💰 Deposit now to unlock signals! 👇")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💰 Deposit", url=AFF_LINK_BASE + user_id))
        bot.send_message(message.chat.id, "Tap below to continue! 🚀", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❓ Hmm... You’re all set! 🎉  \n🎮 Choose a game to get your next signal! 👇")
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("🎮 Aviator Signals", callback_data='aviator'),
                   InlineKeyboardButton("💎 Mines Signals", callback_data='mines'))
        bot.send_message(message.chat.id, "Select your game! 🚀", reply_markup=markup)

if __name__ == '__main__':
    print("Bot started!")
    bot.polling(none_stop=True)
