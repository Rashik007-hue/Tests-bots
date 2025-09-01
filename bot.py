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
    return "Fuck You,,Bot is not alive"

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

# ✅ Luhn Algorithm
def luhn(card):
    nums = [int(x) for x in card]
    return (sum(nums[-1::-2]) + sum(sum(divmod(2 * x, 10)) for x in nums[-2::-2])) % 10 == 0

# ✅ Generate credit card number
def generate_card(bin_format):
    bin_format = bin_format.lower()
    if len(bin_format) < 16:
        bin_format += "x" * (16 - len(bin_format))
    else:
        bin_format = bin_format[:16]
    while True:
        cc = ''.join(str(random.randint(0, 9)) if x == 'x' else x for x in bin_format)
        if luhn(cc):
            return cc

# ✅ Generate card info block
def generate_output(bin_input, username):
    parts = bin_input.split("|")
    bin_format = parts[0] if len(parts) > 0 else ""
    mm_input = parts[1] if len(parts) > 1 and parts[1] != "xx" else None
    yy_input = parts[2] if len(parts) > 2 and parts[2] != "xxxx" else None
    cvv_input = parts[3] if len(parts) > 3 and parts[3] != "xxx" else None

    bin_clean = re.sub(r"[^\d]", "", bin_format)[:6]

    if not bin_clean.isdigit() or len(bin_clean) < 6:
        return f"❌ Invalid BIN provided.\n\nExample:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>"

    scheme = "MASTERCARD" if bin_clean.startswith("5") else "VISA" if bin_clean.startswith("4") else "UNKNOWN"
    ctype = "DEBIT" if bin_clean.startswith("5") else "CREDIT" if bin_clean.startswith("4") else "UNKNOWN"

    cards = []
    start = time.time()
    for _ in range(10):
        cc = generate_card(bin_format)
        mm = mm_input if mm_input else str(random.randint(1, 12)).zfill(2)
        yy_full = yy_input if yy_input else str(random.randint(2026, 2032))
        yy = yy_full[-2:]
        cvv = cvv_input if cvv_input else str(random.randint(100, 999))
        cards.append(f"<code>{cc}|{mm}|{yy}|{cvv}</code>")
    elapsed = round(time.time() - start, 3)

    card_lines = "\n".join(cards)

    text = f"""<b>───────────────</b>
<b>Info</b> - ↯ {scheme} - {ctype}
<b>───────────────</b>
<b>Bin</b> - ↯ {bin_clean} |<b>Time</b> - ↯ {elapsed}s
<b>Input</b> - ↯ <code>{bin_input}</code>
<b>───────────────</b>
{card_lines}
<b>───────────────</b>
<b>Requested By</b> - ↯ @{username} [Free]
"""
    return text

# ✅ /start command
@bot.message_handler(commands=['start'])
def start_handler(message):
    # Save user ID
    user_id = str(message.from_user.id)
    with open("users.txt", "a+") as f:
        f.seek(0)
        if user_id not in f.read().splitlines():
            f.write(user_id + "\n")

    # Response message
    text = (
       "🤖 Bot Status: Active ✅\n\n"
        "📢 For announcements and updates, join us 👉 [here](https://t.me/TrickHubBD)\n\n"
        "💡 Tip: To use 𝒁𝒆𝒓𝒐𝑶𝒏𝑮𝒆𝒏 ∞ in your group, make sure I'm added as admin."
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# ✅ /gen command
@bot.message_handler(commands=['gen'])
def gen_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ Example:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>", parse_mode="HTML")

    bin_input = parts[1].strip()
    username = message.from_user.username or "anonymous"
    text = generate_output(bin_input, username)

    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("Re-Generate ♻️", callback_data=f"again|{bin_input}"))
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=btn)

# ✅ /gen button callback
@bot.callback_query_handler(func=lambda call: call.data.startswith("again|"))
def again_handler(call):
    bin_input = call.data.split("|", 1)[1]
    username = call.from_user.username or "anonymous"
    text = generate_output(bin_input, username)

    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("Re-Generate ♻️", callback_data=f"again|{bin_input}"))

    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text,
                              parse_mode="HTML",
                              reply_markup=btn)
    except:
        bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=btn)

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
