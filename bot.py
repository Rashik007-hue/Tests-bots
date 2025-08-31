from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading
import os
import json
import random
import string
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

# Run Flask in background
def run():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

threading.Thread(target=run).start()

# Load conversation categories
with open("conversation.json", "r", encoding="utf-8") as f:
    categories = json.load(f)
all_replies = sum(categories.values(), [])

# Exact phrase trigger → reply map
conversation_map = {
    "hi": "Hi hi! Lovely yahan hai aapke liye 💖",
    "hello": "Hello ji! Kaise ho aap? 😊",
    "kaise ho": "Main bilkul mast hoon, aap kaise ho? 😄",
    "kya kar rahe ho": "Bas aapka intezaar kar rahi hoon ❤️",
    "love you": "Main bhi aapko pyar karti hoon 😘",
    # ... keep all other unique entries
}

# Message History
user_msg_log = {}

# /start command
@app.on_message(filters.command("start"))
def start(client, message):
    user = message.from_user.first_name
    message.reply_text(
        f"👋 Namastee {user} ji!\n"
        f"Main Lovely hoon — aapki pyari baat-cheet wali dost 💬❤️\n"
        f"Main @{CHANNEL_USERNAME} se judi hoon — zarur join karein 🎬\n\n"
        f"📺 Channel: https://t.me/{CHANNEL_USERNAME}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📺 Channel Join Karein", url=f"https://t.me/{CHANNEL_USERNAME}")
        ]])
    )

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

    # Exact triggers
    for keyword, reply in conversation_map.items():  
        if keyword in text:  
            message.reply_text(reply)  
            return  

    # Fallback replies
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
        # /pass_gen command
@app.on_message(filters.command("pass_gen"))
def generate_password(client, message):
    try:
        # Default password length
        length = 12

        # Allow user to specify length: /pass_gen 20
        if len(message.command) > 1:
            length = int(message.command[1])
            if length < 6:
                length = 6
            elif length > 50:
                length = 50

        # Characters to use in password
        chars = string.ascii_letters + string.digits + string.punctuation
        password = "".join(random.choice(chars) for _ in range(length))

        # Send the password to user
        message.reply_text(f"🔐 Your random password:\n`{password}`", parse_mode="markdown")
    
    except ValueError:
        message.reply_text("⚠️ Please provide a valid number for password length.\nExample: /pass_gen 16")
    except Exception as e:
        message.reply_text(f"⚠️ Something went wrong: {e}")

# Launch the bot
app.run()
