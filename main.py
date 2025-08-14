import json
import os
import random
import time
import threading
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# Import and start keep_alive
from keep_alive import keep_alive
keep_alive()

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive"

@app.route('/postback', methods=['GET', 'POST'])
def postback():
    click_id = request.args.get('click_id')  # {sub1} from link
    event_id = request.args.get('status')    # {event_id} for event type
    date = request.args.get('payout')        # {date} as timestamp proxy
    print(f"DEBUG: Postback received at {time.strftime('%H:%M:%S', time.localtime())}: click_id={click_id}, event_id={event_id}, date={date}")
    
    if click_id and event_id:
        try:
            user_id = str(click_id)
            
            load_users()
            if user_id not in users:
                users[user_id] = {'registered': False, 'deposited': False}
            
            print(f"DEBUG: Before update - User {user_id} status: {users.get(user_id, {})}")
            
            event_lower = event_id.lower()
            if event_lower in ['reg', 'registration', 'reg_complete', 'register', 'signup', 'lead', 'ftd']:
                users[user_id]['registered'] = True
                print(f"DEBUG: User {user_id} marked as registered")
            elif event_lower in ['dep', 'deposit', 'first_deposit', 'payout'] and date:
                users[user_id]['deposited'] = True
                print(f"DEBUG: User {user_id} marked as deposited")
            elif len(event_id) == 36 and '-' in event_id and date:  # UUID check
                users[user_id]['registered'] = True
                print(f"DEBUG: User {user_id} marked as registered (UUID detected)")
            else:
                print(f"DEBUG: Unknown event_id: {event_id}, no action taken")
            
            save_users()
            print(f"DEBUG: After update - User {user_id} status: {users.get(user_id, {})}")
        except Exception as e:
            print(f"DEBUG: Postback error: {e}")
    else:
        print(f"DEBUG: Missing parameters - click_id={click_id}, event_id={event_id}")
    return 'OK', 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask).start()

# Use environment variables
TOKEN = os.environ.get('TOKEN', '7774262573:AAFrdmqRzSSnUF7jEtSreqMVLdLMYbC3Oko')
bot = telebot.TeleBot(TOKEN)
CHAT_ID = int(os.environ.get('CHAT_ID', '-1002889312280'))
AFF_LINK_BASE = os.environ.get('AFF_LINK_BASE', 'https://1wvlau.life/?open=register&p=koqg&sub1=')
IMAGE_PATH = '1.jpg'
PROMO_CODE = os.environ.get('PROMO_CODE', 'BETWIN190')
USERS_FILE = os.environ.get('USERS_FILE', 'users.json')
users = {}

def load_users():
    global users
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
                users = {str(k): v for k, v in users.items()}
        else:
            users = {}
        print(f"DEBUG: Loaded users at {time.strftime('%H:%M:%S', time.localtime())}: {users}")
    except Exception as e:
        print(f"DEBUG: Error loading users: {e}")
        users = {}

def save_users():
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        print(f"DEBUG: Saved users at {time.strftime('%H:%M:%S', time.localtime())}: {users}")
    except Exception as e:
        print(f"DEBUG: Error saving users: {e}")

def generate_crash_multiplier():
    if random.random() <= 0.8:
        return round(random.uniform(1.3, 2.5), 2)
    else:
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
        if game == 'aviator':
            print(f"DEBUG: Sending feedback to CHAT_ID {CHAT_ID}: ✅ GREEN ({multiplier}x)")
            bot.send_message(CHAT_ID, f"✅ GREEN ({multiplier}x)")
        else:
            print(f"DEBUG: Sending feedback to CHAT_ID {CHAT_ID}: ✅ GREEN ({multiplier}x)")
            bot.send_message(CHAT_ID, f"✅ GREEN ({multiplier}x)")
    except Exception as e:
        print(f"DEBUG: Error sending feedback: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    user_id = str(user.id)
    load_users()
    if user_id not in users:
        users[user_id] = {'registered': False, 'deposited': False}
        save_users()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton('📌 REGISTER'))
    with open(IMAGE_PATH, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=f"🎉 Hello, @{user.username}! 🌟 Welcome to SureWin Signal Bot! 🚀\nBoost your wins in 1win Aviator and Mines! ❤️", parse_mode='HTML')
    bot.send_message(message.chat.id, "Start your winning journey! 🎯 Click below! 🌈", reply_markup=markup)

@bot.message_handler(commands=['debug'])
def debug_status(message):
    user_id = str(message.from_user.id)
    load_users()
    status = users.get(user_id, {'registered': False, 'deposited': False})
    bot.send_message(message.chat.id, f"🛠 Debug: User {user_id} - Registered: {status['registered']}, Deposited: {status['deposited']}")

@bot.message_handler(commands=['testgroup'])
def test_group(message):
    try:
        print(f"DEBUG: Testing group message to CHAT_ID {CHAT_ID}")
        bot.send_message(CHAT_ID, "🎉 Test message - Bot is rocking! 🚀")
        bot.send_photo(CHAT_ID, open(IMAGE_PATH, 'rb'), caption="🌟 Test photo! ✨")
    except Exception as e:
        print(f"DEBUG: Error testing group: {e}")
        bot.send_message(message.chat.id, f"❌ Oops! Group send failed: {e}")

@bot.message_handler(func=lambda m: m.text == '📌 REGISTER')
def handle_register(message):
    user_id = str(message.from_user.id)
    reg_link = AFF_LINK_BASE + user_id
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎁 Register Now", url=reg_link))
    bot.send_message(message.chat.id, f"📝 Get started! 🎁 Use promo code: <b>{PROMO_CODE}</b>\n❗️ If you see an old account, log out and click 'Register Now' again. ⏳ Then, hit '✅ CHECK REGISTRATION'! 🌟", parse_mode='HTML', reply_markup=markup)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton('✅ CHECK REGISTRATION'))
    bot.send_message(message.chat.id, "Ready to win? Check your status! 🚀", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '✅ CHECK REGISTRATION')
def check_registered(message):
    user_id = str(message.from_user.id)
    load_users()
    print(f"DEBUG: Checking registration for user {user_id} at {time.strftime('%H:%M:%S', time.localtime())}: {users.get(user_id, {})}")
    
    if users.get(user_id, {}).get('registered', False):
        bot.send_message(message.chat.id, "🎉 Registration complete! Woho! 🌟 Time to deposit and unlock the fun! 💸")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton('💰 DEPOSIT'))
        bot.send_message(message.chat.id, "Deposit to play! 🚀", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Registration pending! Ensure you used the link, completed registration, and waited 2-3 minutes ⏳")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton('✅ CHECK REGISTRATION'))
        bot.send_message(message.chat.id, "Try again! 🔄", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '💰 DEPOSIT')
def handle_deposit(message):
    user_id = str(message.from_user.id)
    load_users()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🌐 Deposit Now", url=AFF_LINK_BASE + user_id))
    bot.send_message(message.chat.id, "💰 Confirm you’re human with any top-up!\n🔸 Activate your account with your first deposit—funds credited to play and WIN! 🌟\n● After depositing, click: «🔍 CHECK DEPOSIT» ⏳")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton('🔍 CHECK DEPOSIT'))
    bot.send_message(message.chat.id, "Fund your account! 🚀", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '🔍 CHECK DEPOSIT')
def check_deposited(message):
    user_id = str(message.from_user.id)
    load_users()
    if not users.get(user_id, {}).get('registered', False):
        bot.send_message(message.chat.id, "❌ Register first! 📌")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton('📌 REGISTER'))
        bot.send_message(message.chat.id, "Start here! 🌟", reply_markup=markup)
    elif users.get(user_id, {}).get('deposited', False):
        bot.send_message(message.chat.id, "🎉 Deposit confirmed! Woho! 💸 Ready to play! 🌟")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(telebot.types.KeyboardButton('🎮 AVIATOR SIGNALS'), telebot.types.KeyboardButton('💎 MINES SIGNALS'))
        bot.send_message(message.chat.id, "Choose your game! 🚀", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Deposit pending! Fund your account and wait 2-3 minutes ⏳")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton('🔍 CHECK DEPOSIT'))
        bot.send_message(message.chat.id, "Check again! 🔄", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '🎮 AVIATOR SIGNALS')
def aviator_signal(message):
    user_id = str(message.from_user.id)
    load_users()
    if not (users.get(user_id, {}).get('registered', False) and users.get(user_id, {}).get('deposited', False)):
        bot.send_message(message.chat.id, "❌ Complete registration and deposit first! 📌💰")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton('📌 REGISTER'), telebot.types.KeyboardButton('💰 DEPOSIT'))
        bot.send_message(message.chat.id, "Get started! 🌟", reply_markup=markup)
        return
    previous_multiplier = round(random.uniform(1.0, 1.87), 2)
    current_multiplier = generate_crash_multiplier()
    full_message = (
        "🎯 Aviator Signal Ready! 🎮\n"
        f"📱 Play: <a href='https://1wvlau.life/?open=register&p=koqg'>Here</a>\n\n"
        f"👉 Enter after {previous_multiplier}x\n"
        f"💰 Exit at {current_multiplier}x\n\n"
        "🛡️ Up to 2 protections\n"
        f"💸 Platform: <a href='https://1wvlau.life/?open=register&p=koqg'>Here</a>"
    )
    try:
        print(f"DEBUG: Sending Aviator signal to CHAT_ID {CHAT_ID}")
        with open(IMAGE_PATH, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo, caption=full_message, parse_mode='HTML')
        threading.Timer(180, send_feedback, args=(current_multiplier, 'aviator')).start()
        bot.send_message(message.chat.id, "Signal sent to group! 🎉 Check it! 🚀")
    except Exception as e:
        print(f"DEBUG: Error sending Aviator signal: {e}")
        bot.send_message(message.chat.id, f"❌ Signal failed: {e}")

@bot.message_handler(func=lambda m: m.text == '💎 MINES SIGNALS')
def mines_signal(message):
    user_id = str(message.from_user.id)
    load_users()
    if not (users.get(user_id, {}).get('registered', False) and users.get(user_id, {}).get('deposited', False)):
        bot.send_message(message.chat.id, "❌ Complete registration and deposit first! 📌💰")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton('📌 REGISTER'), telebot.types.KeyboardButton('💰 DEPOSIT'))
        bot.send_message(message.chat.id, "Get started! 🌟", reply_markup=markup)
        return
    num_mines, pos_str, multiplier = generate_mines_signal()
    full_message = (
        "🎯 Mines Signal Ready! 💎\n"
        f"📱 Play: <a href='https://1wvlau.life/?open=register&p=koqg'>Here</a>\n\n"
        f"Set Mines: {num_mines}\n"
        f"Click Sequence: {pos_str}\n"
        f"💰 Cash out at {multiplier}x\n\n"
        "🛡️ Up to 2 protections\n"
        f"💸 Platform: <a href='https://1wvlau.life/?open=register&p=koqg'>Here</a>"
    )
    try:
        print(f"DEBUG: Sending Mines signal to CHAT_ID {CHAT_ID}")
        with open(IMAGE_PATH, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo, caption=full_message, parse_mode='HTML')
        threading.Timer(150, send_feedback, args=(multiplier, 'mines')).start()
        bot.send_message(message.chat.id, "Signal sent to group! 🎉 Check it! 🚀")
    except Exception as e:
        print(f"DEBUG: Error sending Mines signal: {e}")
        bot.send_message(message.chat.id, f"❌ Signal failed: {e}")

# Default handler for random messages
@bot.message_handler(func=lambda message: True)
def handle_random_message(message):
    user_id = str(message.from_user.id)
    load_users()
    status = users.get(user_id, {'registered': False, 'deposited': False})
    
    if not status.get('registered', False):
        bot.send_message(message.chat.id, "❓ Oops! Unrecognized input! 🎉 Register to begin! 📌")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton('📌 REGISTER'))
        bot.send_message(message.chat.id, "Click to start! 🌟", reply_markup=markup)
    elif not status.get('deposited', False):
        bot.send_message(message.chat.id, "❓ Not sure? 🎉 You’re registered! 💰 Deposit next! 🌈")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton('💰 DEPOSIT'))
        bot.send_message(message.chat.id, "Deposit now! 🚀", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❓ Hmm? 🎉 You’re all set! 🎮💎 Play now! 🌟")
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.row(telebot.types.KeyboardButton('🎮 AVIATOR SIGNALS'), telebot.types.KeyboardButton('💎 MINES SIGNALS'))
        bot.send_message(message.chat.id, "Choose your game! 🚀", reply_markup=markup)

bot.polling()
