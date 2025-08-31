import os
import re
import time
import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# 🔐 Bot Config
TOKEN = os.environ.get("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "TrickHubBD")
bot = telebot.TeleBot(TOKEN)

# 🌐 Flask App
app = Flask(__name__)

# ===========================
# 🎯 Luhn + Gen Functions
# ===========================
def luhn(card):
    nums = [int(x) for x in card]
    return (sum(nums[-1::-2]) + sum(sum(divmod(2 * x, 10)) for x in nums[-2::-2])) % 10 == 0

def generate_card(bin_format):
    if len(bin_format) < 16:
        bin_format += "x" * (16 - len(bin_format))
    else:
        bin_format = bin_format[:16]

    while True:
        cc = "".join(str(random.randint(0, 9)) if x.lower() == "x" else x for x in bin_format)
        if luhn(cc):
            return cc

def generate_output(bin_input, username):
    parts = bin_input.split("|")
    bin_format = parts[0] if len(parts) > 0 else ""
    mm_input = parts[1] if len(parts) > 1 and parts[1] != "xx" else None
    yy_input = parts[2] if len(parts) > 2 and parts[2] != "xxxx" else None
    cvv_input = parts[3] if len(parts) > 3 and parts[3] != "xxx" else None

    bin_clean = re.sub(r"[^\d]", "", bin_format)[:6]
    if not bin_clean.isdigit() or len(bin_clean) < 6:
        return f"❌ Invalid BIN.\n\nExample:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>"

    scheme = "MASTERCARD" if bin_clean.startswith("5") else "VISA" if bin_clean.startswith("4") else "UNKNOWN"

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
<b>Info</b> - ↯ {scheme}
<b>───────────────</b>
<b>Bin</b> - ↯ {bin_clean} | <b>Time</b> - ↯ {elapsed}s
<b>Input</b> - ↯ <code>{bin_input}</code>
<b>───────────────</b>
{chr(10).join(cards)}
<b>───────────────</b>
<b>Requested By</b> - ↯ @{username}
"""

# ===========================
# 🎯 Commands
# ===========================
@bot.message_handler(commands=['start'])
def start_handler(message):
    user = message.from_user.first_name
    bot.reply_to(message,
        f"👋 Hello {user}!\n"
        f"Main *Lovely Gen Bot* hoon 💖\n\n"
        f"📺 Join: https://t.me/{CHANNEL_USERNAME}\n\n"
        f"Type `/gen BIN|MM|YY|CVV` to generate cards.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📺 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
        ]])
    )

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

# ===========================
# 🌐 Webhook Setup
# ===========================
@app.route("/" + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}")
    return "Webhook set!", 200
