# 📦 Imports
import os
import re
import time
import random
import threading
import requests
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔐 Environment Variables
TOKEN = os.environ.get("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")
OWNER_ID = int(os.environ.get("OWNER_ID", 6321618547))
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "TrickHubBD")  # without @

# 🤖 Telebot Client
bot = telebot.TeleBot(TOKEN)

# 🌐 Flask App (for keep-alive on Heroku/Railway)
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "❤️ Lovely System Bot is Live!"

def run():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

threading.Thread(target=run).start()

# 📂 Users File
USERS_FILE = "users.txt"

def save_user(user_id):
    user_id = str(user_id)
    with open(USERS_FILE, "a+") as f:
        f.seek(0)
        if user_id not in f.read().splitlines():
            f.write(user_id + "\n")

# ===========================
# 🎯 Utility Functions
# ===========================

# ✅ Luhn Algorithm
def luhn(card):
    nums = [int(x) for x in card]
    return (sum(nums[-1::-2]) + sum(sum(divmod(2 * x, 10)) for x in nums[-2::-2])) % 10 == 0

# ✅ Generate Credit Card
def generate_card(bin_format):
    if len(bin_format) < 16:
        bin_format += "x" * (16 - len(bin_format))
    else:
        bin_format = bin_format[:16]
    while True:
        cc = ''.join(str(random.randint(0, 9)) if x == 'x' else x for x in bin_format)
        if luhn(cc):
            return cc

# ✅ Generate Card Output
def generate_output(bin_input, username):
    parts = bin_input.split("|")
    bin_format = parts[0] if len(parts) > 0 else ""
    mm_input = parts[1] if len(parts) > 1 and parts[1] != "xx" else None
    yy_input = parts[2] if len(parts) > 2 and parts[2] != "xxxx" else None
    cvv_input = parts[3] if len(parts) > 3 and parts[3] != "xxx" else None

    bin_clean = re.sub(r"[^\d]", "", bin_format)[:6]
    if not bin_clean.isdigit() or len(bin_clean) < 6:
        return f"❌ Invalid BIN.\nExample:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>"

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

    return f"""<b>───────────────</b>
<b>Info</b> - ↯ {scheme} - {ctype}
<b>───────────────</b>
<b>Bin</b> - ↯ {bin_clean} | <b>Time</b> - ↯ {elapsed}s
<b>Input</b> - ↯ <code>{bin_input}</code>
<b>───────────────</b>
{chr(10).join(cards)}
<b>───────────────</b>
<b>Requested By</b> - ↯ @{username} [Free]
"""

# ===========================
# 🎯 Commands
# ===========================

# ✅ /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    save_user(message.from_user.id)
    user = message.from_user.first_name
    bot.reply_to(message,
        f"👋 Namaste {user}!\n"
        f"Main *Lovely System Bot* hoon — aapki pyari dost 💬❤️\n"
        f"Main @{CHANNEL_USERNAME} se judi hoon — zarur join karein 🎬\n\n"
        f"📺 Channel: https://t.me/{CHANNEL_USERNAME}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📺 Channel Join Karein", url=f"https://t.me/{CHANNEL_USERNAME}")
        ]])
    )

# ✅ /help
@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.reply_to(message, """📖 *Available Commands*

/gen <bin> ➝ Generate CCs  
/ask <query> ➝ Ask AI  
/fake <country_code> ➝ Fake Address  
/country ➝ Supported Countries  
/broadcast <msg> ➝ Broadcast (Owner Only)  

⚡ Example:
`/gen 545231xxxxxxxxxx|03|27|xxx`
""", parse_mode="Markdown")

# ✅ /gen
@bot.message_handler(commands=['gen'])
def gen_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ Example:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>", parse_mode="HTML")

    bin_input = parts[1].strip()
    username = message.from_user.username or "anonymous"
    text = generate_output(bin_input, username)

    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("♻️ Re-Generate", callback_data=f"again|{bin_input}"))
    bot.reply_to(message, text, parse_mode="HTML", reply_markup=btn)

# 🔁 /gen button
@bot.callback_query_handler(func=lambda call: call.data.startswith("again|"))
def again_handler(call):
    bin_input = call.data.split("|", 1)[1]
    username = call.from_user.username or "anonymous"
    text = generate_output(bin_input, username)

    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("♻️ Re-Generate", callback_data=f"again|{bin_input}"))

    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text,
                              parse_mode="HTML",
                              reply_markup=btn)
    except:
        bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=btn)

# ✅ /ask
@bot.message_handler(commands=['ask'])
def ask_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "❓ Usage: `/ask your question`", parse_mode="Markdown")
    prompt = parts[1]
    try:
        res = requests.get(f"https://gpt-3-5.apis-bj-devs.workers.dev/?prompt={prompt}")
        data = res.json()
        reply = data.get("reply", "❌ API error.")
        bot.reply_to(message, f"*{reply}*", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: `{e}`", parse_mode="Markdown")

# ✅ /fake
@bot.message_handler(commands=['fake'])
def fake_handler(message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ Example:\n`/fake us`", parse_mode="Markdown")
    code = parts[1].lower()
    supported = ["us","in","uk","ca","au","bd","pk","fr","de","jp","br","es"]
    if code not in supported:
        return bot.reply_to(message, "❌ Invalid or unsupported country.", parse_mode="Markdown")
    try:
        res = requests.get(f"https://randomuser.me/api/?nat={code}").json()
        user = res['results'][0]
        addr = user['location']
        msg = f"""📦 *Fake Address Info*

👤 *Name:* `{user['name']['first']} {user['name']['last']}`
🏠 *Address:* `{addr['street']['number']} {addr['street']['name']}`
🏙️ *City:* `{addr['city']}`
🗺️ *State:* `{addr['state']}`
📮 *ZIP:* `{addr['postcode']}`
🌐 *Country:* `{addr['country']}`"""
        bot.reply_to(message, msg, parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ API error, try later.", parse_mode="Markdown")

# ✅ /country
@bot.message_handler(commands=['country'])
def country_handler(message):
    text = """🌍 *Supported Countries:*  
US, IN, UK, CA, AU, BD, PK, FR, DE, JP, BR, ES"""
    bot.reply_to(message, text, parse_mode="Markdown")

# ✅ /broadcast
@bot.message_handler(commands=['broadcast'])
def broadcast_handler(message):
    if message.from_user.id != OWNER_ID:
        return bot.reply_to(message, "🚫 Not authorized.")
    try:
        _, text = message.text.split(" ", 1)
    except:
        return bot.reply_to(message, "⚠️ Usage:\n`/broadcast message`", parse_mode="Markdown")
    try:
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
    except:
        return bot.reply_to(message, "❌ No users found.")
    sent, fail = 0, 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 *Broadcast:*\n\n{text}", parse_mode="Markdown")
            sent += 1
        except:
            fail += 1
    bot.reply_to(message, f"✅ Done!\n🟢 Sent: `{sent}`\n🔴 Failed: `{fail}`", parse_mode="Markdown")

# ===========================
# 🚀 Run Bot
# ===========================
print("🤖 Lovely System Bot is running...")
bot.polling()
