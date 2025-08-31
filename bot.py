from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading
import os
import json
import random

# Environment Variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "youtuber02alltypemovies")

# Pyrogram Bot
app = Client("Hosted_By_Vercel_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask App
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "❤️ Lovely Bot is Live!"

def run():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

threading.Thread(target=run).start()

# Load conversation categories
with open("conversation.json", "r", encoding="utf-8") as f:
    categories = json.load(f)
all_replies = sum(categories.values(), [])

conversation_map = {
    "hi": "Hi hi! Lovely yahan hai aapke liye 💖",
    "hello": "Hello ji! Kaise ho aap? 😊",
    "kaise ho": "Main bilkul mast hoon, aap kaise ho? 😄",
    "kya kar rahe ho": "Bas aapka intezaar kar rahi hoon ❤️",
    "love you": "Main bhi aapko pyar karti hoon 😘",
}

user_msg_log = {}

# /start command
@app.on_message(filters.command("start"))
def start(client, message):
    user = message.from_user.first_name
    message.reply_text(
        f"👋 Namaste {user} ji!\n"
        f"Main Lovely hoon — aapki pyari baat-cheet wali dost 💬❤️\n"
        f"Main @{CHANNEL_USERNAME} se judi hoon — zarur join karein 🎬\n\n"
        f"📺 Channel: https://t.me/{CHANNEL_USERNAME}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📺 Channel Join Karein", url=f"https://t.me/{CHANNEL_USERNAME}")
        ]])
    )

# Luhn algorithm CC generator
def generate_cc_number(prefix="400000", length=16):
    cc_number = [int(x) for x in prefix]
    while len(cc_number) < (length - 1):
        cc_number.append(random.randint(0, 9))
    def luhn_checksum(number):
        sum_ = 0
        reverse_digits = number[::-1]
        for i, digit in enumerate(reverse_digits):
            if i % 2 == 0:
                sum_ += digit
            else:
                d = digit * 2
                if d > 9:
                    d -= 9
                sum_ += d
        return (10 - (sum_ % 10)) % 10
    cc_number.append(luhn_checksum(cc_number))
    return "".join(map(str, cc_number))

# /gen command with optional count
@app.on_message(filters.command("gen"))
def generate_cc(client, message):
    try:
        count = 10  # default
        if len(message.command) > 1:
            arg = message.command[1].strip()
            if arg.isdigit():
                count = int(arg)
                if count < 1:
                    count = 1
                elif count > 50:
                    count = 50
            else:
                message.reply_text("⚠️ Please provide a valid number.\nExample: /gen 10")
                return
        cc_list = "\n".join(generate_cc_number() for _ in range(count))
        message.reply_text(f"💳 Here are {count} valid CC numbers (Luhn):\n`{cc_list}`", parse_mode="Markdown")
    except Exception as e:
        message.reply_text(f"⚠️ Something went wrong: {e}")

# Conversation Handler
@app.on_message(filters.text & filters.private)
def handle_private(_, message):
    text = message.text.lower().strip()
    if message.from_user.is_bot or text.startswith("/"):  
        return  

    user_id = message.from_user.id  
    if user_id not in user_msg_log:  
        user_msg_log[user_id] = {}  
    user_msg_log[user_id][text] = user_msg_log[user_id].get(text, 0) + 1  
    if user_msg_log[user_id][text] > 2:  
        return  

    for keyword, reply in conversation_map.items():  
        if keyword in text:  
            message.reply_text(reply)  
            return  

    if any(w in text for w in ["love", "crush", "miss"]):  
        reply = random.choice(categories.get("love", all_replies))  
    elif any(w in text for w in ["sad", "cry", "hurt"]):  
        reply = random.choice(categories.get("sad", all_replies))  
    elif any(w in text for w in ["happy", "great", "awesome"]):  
        reply = random.choice(categories.get("happy", all_replies))  
    elif any(w in text for w in ["hi", "hello", "kaise", "kya", "bored"]):  
        reply = random.choice(categories.get("daily", all_replies))  
    elif any(w in text for w in ["masti", "party", "enjoy"]):  
        reply = random.choice(categories.get("fun", all_replies))  
    else:  
        reply = random.choice(all_replies)  

    message.reply_text(reply)

# Welcome message for new members
@app.on_chat_member_updated()
def welcome(_, update: ChatMemberUpdated):
    if update.new_chat_member.status == "member" and not update.new_chat_member.user.is_bot:
        name = update.new_chat_member.user.first_name
        app.send_message(
            chat_id=update.chat.id,
            text=f"🎀 Welcome {name} ji!\nMain Lovely hoon — aapki chat wali dost 💁‍♀️\nMasti aur baat dono chalegi yahaan ❤️"
        )

# Launch the bot
app.run()
# Luhn algorithm CC generator
def generate_cc_number(prefix="400000", length=16):
    cc_number = [int(x) for x in prefix]
    while len(cc_number) < (length - 1):
        cc_number.append(random.randint(0, 9))
    def luhn_checksum(number):
        sum_ = 0
        reverse_digits = number[::-1]
        for i, digit in enumerate(reverse_digits):
            if i % 2 == 0:
                sum_ += digit
            else:
                d = digit * 2
                if d > 9:
                    d -= 9
                sum_ += d
        return (10 - (sum_ % 10)) % 10
    cc_number.append(luhn_checksum(cc_number))
    return "".join(map(str, cc_number))

# /gen command with optional count
@app.on_message(filters.command("gen"))
def generate_cc(client, message):
    try:
        count = 10  # default
        if len(message.command) > 1:
            arg = message.command[1].strip()
            if arg.isdigit():
                count = int(arg)
                if count < 1:
                    count = 1
                elif count > 50:
                    count = 50
            else:
                message.reply_text("⚠️ Please provide a valid number.\nExample: /gen 10")
                return
        cc_list = "\n".join(generate_cc_number() for _ in range(count))
        message.reply_text(f"💳 Here are {count} valid CC numbers (Luhn):\n`{cc_list}`", parse_mode="markdown")
    except Exception as e:
        message.reply_text(f"⚠️ Something went wrong: {e}")

# Conversation Handler
@app.on_message(filters.text & filters.private)
def handle_private(_, message):
    text = message.text.lower().strip()
    if message.from_user.is_bot or text.startswith("/"):  
        return  

    user_id = message.from_user.id  
    if user_id not in user_msg_log:  
        user_msg_log[user_id] = {}  
    user_msg_log[user_id][text] = user_msg_log[user_id].get(text, 0) + 1  
    if user_msg_log[user_id][text] > 2:  
        return  

    for keyword, reply in conversation_map.items():  
        if keyword in text:  
            message.reply_text(reply)  
            return  

    if any(w in text for w in ["love", "crush", "miss"]):  
        reply = random.choice(categories.get("love", all_replies))  
    elif any(w in text for w in ["sad", "cry", "hurt"]):  
        reply = random.choice(categories.get("sad", all_replies))  
    elif any(w in text for w in ["happy", "great", "awesome"]):  
        reply = random.choice(categories.get("happy", all_replies))  
    elif any(w in text for w in ["hi", "hello", "kaise", "kya", "bored"]):  
        reply = random.choice(categories.get("daily", all_replies))  
    elif any(w in text for w in ["masti", "party", "enjoy"]):  
        reply = random.choice(categories.get("fun", all_replies))  
    else:  
        reply = random.choice(all_replies)  

    message.reply_text(reply)

# Welcome message for new members
@app.on_chat_member_updated()
def welcome(_, update: ChatMemberUpdated):
    if update.new_chat_member.status == "member" and not update.new_chat_member.user.is_bot:
        name = update.new_chat_member.user.first_name
        app.send_message(
            chat_id=update.chat.id,
            text=f"🎀 Welcome {name} ji!\nMain Lovely hoon — aapki chat wali dost 💁‍♀️\nMasti aur baat dono chalegi yahaan ❤️"
        )

# Launch the bot
app.run()
