import os
import re
import time
import random
from flask import Flask, request
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Update

# 🔐 Config
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "TrickHubBD")

# 🤖 Pyrogram Bot
app = Client(
    "lovely_gen_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# 🌐 Flask App (Webhook endpoint)
flask_app = Flask(__name__)

# =========================
# 🎯 Luhn + Gen Functions
# =========================
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

# =========================
# 🎯 Commands
# =========================
@app.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user.first_name
    await message.reply_text(
        f"👋 Hello {user}!\n"
        f"Main *Lovely Gen Bot* hoon 💖\n\n"
        f"📺 Join: https://t.me/{CHANNEL_USERNAME}\n\n"
        f"Type `/gen BIN|MM|YY|CVV` to generate cards.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📺 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
        ]]),
        parse_mode="Markdown"
    )

@app.on_message(filters.command("gen"))
async def gen_handler(client, message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return await message.reply_text(
            "⚠️ Example:\n<code>/gen 545231xxxxxxxxxx|03|27|xxx</code>",
            parse_mode="HTML"
        )

    bin_input = parts[1].strip()
    username = message.from_user.username or "anonymous"
    text = generate_output(bin_input, username)

    btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("♻️ Re-Generate", callback_data=f"again|{bin_input}")]]
    )
    await message.reply_text(text, parse_mode="HTML", reply_markup=btn)

@app.on_callback_query()
async def again_handler(client, callback_query):
    if callback_query.data.startswith("again|"):
        bin_input = callback_query.data.split("|", 1)[1]
        username = callback_query.from_user.username or "anonymous"
        text = generate_output(bin_input, username)

        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("♻️ Re-Generate", callback_data=f"again|{bin_input}")]]
        )
        try:
            await callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=btn)
        except:
            await callback_query.message.reply_text(text, parse_mode="HTML", reply_markup=btn)

# =========================
# 🌐 Flask Webhook
# =========================
@flask_app.route("/")
def home():
    return "Lovely Gen Bot is Live!"

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))).start()
    app.run()
