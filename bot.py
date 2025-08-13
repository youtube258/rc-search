import requests
import telebot
from telebot import types
import html
import os
import json
import time
import random
import string

# ========== CONFIG ==========
BOT_TOKEN = "8491937567:AAH3KXPtBVl6B6OwsSoa8MixhuheWTA0Uy8"
OWNER_ID = 6820574331
API_URL = "https://rc-info-j4tnx.onrender.com/rc={}"  # API endpoint
USERS_FILE = "users.txt"
CREDITS_FILE = "credits.json"
REDEEM_FILE = "redeem_codes.json"  # new file for redeem codes

# Required channels
CHANNELS = ["@snnetwork7", "@snxrajput_bio", "@babitajiii"]

# Default credits
NEW_USER_CREDITS = 1
REFERRAL_BONUS = 2

bot = telebot.TeleBot(BOT_TOKEN)

# ======== Helpers ========
def ensure_files():
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    if not os.path.exists(CREDITS_FILE):
        with open(CREDITS_FILE, "w") as f:
            json.dump({}, f)
    if not os.path.exists(REDEEM_FILE):
        with open(REDEEM_FILE, "w") as f:
            json.dump({}, f)

def save_user_id(user_id: int):
    try:
        ensure_files()
        with open(USERS_FILE, "r") as f:
            ids = {int(x.strip()) for x in f.readlines() if x.strip().isdigit()}
        if user_id not in ids:
            with open(USERS_FILE, "a") as f:
                f.write(f"{user_id}\n")
    except Exception as e:
        print("save_user_id error:", e)

def load_all_users():
    ensure_files()
    with open(USERS_FILE, "r") as f:
        return [int(x.strip()) for x in f.readlines() if x.strip().isdigit()]

def load_credits():
    ensure_files()
    with open(CREDITS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_credits(data):
    with open(CREDITS_FILE, "w") as f:
        json.dump(data, f)

def get_credits(user_id: int):
    if user_id == OWNER_ID:
        return 10**9
    data = load_credits()
    return int(data.get(str(user_id), 0))

def set_credits(user_id: int, amount: int):
    if user_id == OWNER_ID:
        return
    data = load_credits()
    data[str(user_id)] = int(amount)
    save_credits(data)

def add_credits(user_id: int, amount: int):
    if user_id == OWNER_ID:
        return
    data = load_credits()
    cur = int(data.get(str(user_id), 0))
    data[str(user_id)] = cur + int(amount)
    save_credits(data)
    return data[str(user_id)]

# ======== Redeem codes helpers ========
def load_redeem_codes():
    ensure_files()
    with open(REDEEM_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_redeem_codes(data):
    with open(REDEEM_FILE, "w") as f:
        json.dump(data, f)

def generate_code(length=8):
    # Uppercase alnum code
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=length))

# ======== Channel check ========
def user_in_channel(user_id: int, channel_username: str):
    if user_id == OWNER_ID:
        return True
    try:
        member = bot.get_chat_member(channel_username, user_id)
        if hasattr(member, "status"):
            if member.status in ("creator", "administrator", "member", "restricted"):
                return True
        return False
    except Exception as e:
        print(f"verify channel error: {e}")
        return False

def all_channels_joined(user_id: int):
    if user_id == OWNER_ID:
        return True
    for ch in CHANNELS:
        if not user_in_channel(user_id, ch):
            return False
    return True

# ======== Start ========
@bot.message_handler(commands=["start"])
def start_cmd(message):
    ensure_files()
    user_id = message.chat.id
    save_user_id(user_id)

    # Referral
    text = message.text or ""
    parts = text.split()
    if len(parts) >= 2:
        ref = parts[1].strip()
        if ref.isdigit():
            rid = int(ref)
            if rid != user_id:
                add_credits(rid, REFERRAL_BONUS)
                try:
                    bot.send_message(rid, f"🎉 You received +{REFERRAL_BONUS} credits for referring a new user!")
                except:
                    pass

    if get_credits(user_id) == 0 and user_id != OWNER_ID:
        set_credits(user_id, NEW_USER_CREDITS)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔍 Search RC", "ℹ️ About Bot", "👤 My Credit", "💳 Buy Credit")

    ik = types.InlineKeyboardMarkup()
    btns = []
    for ch in CHANNELS:
        btns.append(types.InlineKeyboardButton(text=f"Join {ch}", url=f"https://t.me/{ch.lstrip('@')}"))
    if btns:
        ik.row(*btns)
    ik.add(types.InlineKeyboardButton(text="I have joined ✅", callback_data="verify_join"))

    start_text = (
        "╔════════ 🚗 ════════╗\n"
        "  *Welcome to RC Info Bot*\n"
        "╚══════════════════╝\n\n"
        "💠 *I can fetch vehicle registration details instantly!* \n\n"
        "📌 *Example RC Numbers:*\n`MH20EE7601`\n`DL8CAF5030`\n\n"
        "💬 *Click on* '🔍 Search RC' *below or type the RC number directly.*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⃛͢°‌ ℞₳J₱ɄŦ Ø₱ ] 💮"
    )

    bot.send_message(user_id, start_text, parse_mode="Markdown", reply_markup=markup)
    bot.send_message(user_id, "⚠️ Please join the channels below to use the bot:", reply_markup=ik)

# ======== Buy Credit Button ========
@bot.message_handler(func=lambda m: m.text == "💳 Buy Credit")
def buy_credit(m):
    bot.send_message(
        m.chat.id,
        "💳 To buy credits, please contact: @snxrajput\n\n📌 Payment details will be provided by the owner.",
        parse_mode="HTML"
    )

# ======== View Users (Owner only) ========
@bot.message_handler(commands=["users"])
def view_users(message):
    if message.chat.id != OWNER_ID:
        return
    users = load_all_users()
    count = len(users)
    user_list = "\n".join(str(u) for u in users)
    bot.send_message(
        OWNER_ID,
        f"📊 Total Users: <b>{count}</b>\n\n<pre>{user_list}</pre>",
        parse_mode="HTML"
    )

# ======== Verify Join Callback ========
@bot.callback_query_handler(func=lambda cq: cq.data == "verify_join")
def handle_verify(cq):
    user_id = cq.from_user.id
    missing = [ch for ch in CHANNELS if not user_in_channel(user_id, ch)]
    if not missing:
        bot.answer_callback_query(cq.id, "✅ Verified — you have joined all channels.")
        bot.send_message(user_id, "🎉 Verification successful. You can now search RC numbers.")
    else:
        text = "❌ Verification failed. Please join these channels first:\n"
        for ch in missing:
            text += f"{ch}\n"
        text += "\nThen press *I have joined* again."
        bot.answer_callback_query(cq.id, "Not all channels joined.")
        bot.send_message(user_id, text, parse_mode="Markdown")

# ======== About ========
@bot.message_handler(func=lambda m: m.text == "ℹ️ About Bot")
def about_bot(m):
    bot.send_message(
        m.chat.id,
        "🤖 <b>RC Info Bot</b>\n\n"
        "This bot fetches vehicle registration details using RC number.\n"
        "Data source: API provided by developer.\n\n"
        "Commands:\n"
        "/referral - Get your referral link\n"
        "/mycredit - Check your credits\n"
        "/addcredit - (Owner) Get credits\n"
        "/removecredit - (Owner) remove credit\n"
        "/broadcast - (Owner) Broadcast message\n"
        "/users - (Owner) View all users\n"
        "/makecode - (Owner) Create redeem code\n"
        "/redeem - Redeem a code",
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda m: m.text == "👤 My Credit")
def mycredit_button(m):
    c = get_credits(m.chat.id)
    if m.chat.id == OWNER_ID:
        bot.send_message(m.chat.id, "💳 Your credits: <b>Unlimited (Owner)</b>", parse_mode="HTML")
    else:
        bot.send_message(m.chat.id, f"💳 Your credits: <b>{c}</b>", parse_mode="HTML")

# ======== Referral ========
@bot.message_handler(commands=["referral"])
def referral_cmd(message):
    uid = message.chat.id
    try:
        me = bot.get_me()
        bot_username = me.username
    except:
        bot_username = None
    if bot_username:
        link = f"https://t.me/{bot_username}?start={uid}"
    else:
        link = f"/start {uid}"
    bot.send_message(uid, f"Share this link with friends. For each new user who joins using it, you get +{REFERRAL_BONUS} credits:\n\n{link}")

# ======== Mycredit ========
@bot.message_handler(commands=["mycredit"])
def mycredit_cmd(message):
    uid = message.chat.id
    if uid == OWNER_ID:
        bot.send_message(uid, "💳 Your credits: <b>Unlimited (Owner)</b>", parse_mode="HTML")
        return
    c = get_credits(uid)
    bot.send_message(uid, f"💳 Your credits: <b>{c}</b>\n\n1 search = 1 credit", parse_mode="HTML")

# ======== Owner: Addcredit ========
@bot.message_handler(commands=["addcredit"])
def addcredit_cmd(message):
    if message.chat.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.send_message(OWNER_ID, "Usage: /addcredit <user_id> <credits>")
        return
    try:
        uid = int(parts[1])
        amt = int(parts[2])
        add_credits(uid, amt)
        bot.send_message(OWNER_ID, f"✅ Added {amt} credits to {uid}.")
        try:
            bot.send_message(uid, f"🎁 You received +{amt} credits from the owner. New balance: {get_credits(uid)}")
        except:
            pass
    except Exception as e:
        bot.send_message(OWNER_ID, f"Error: {e}")

# ======== Owner: Removecredit ========
@bot.message_handler(commands=["removecredit"])
def removecredit_cmd(message):
    if message.chat.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.send_message(OWNER_ID, "Usage: /removecredit <user_id> <credits>")
        return
    try:
        uid = int(parts[1])
        amt = int(parts[2])
        data = load_credits()
        cur = int(data.get(str(uid), 0))
        new_amt = max(cur - amt, 0)
        set_credits(uid, new_amt)
        bot.send_message(OWNER_ID, f"✅ Removed {amt} credits from {uid}. New balance: {new_amt}")
        try:
            bot.send_message(uid, f"⚠️ {amt} credits removed by the owner. New balance: {new_amt}")
        except:
            pass
    except Exception as e:
        bot.send_message(OWNER_ID, f"Error: {e}")

# ======== Owner: Broadcast ========
@bot.message_handler(commands=["broadcast"])
def broadcast_cmd(message):
    if message.chat.id != OWNER_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(OWNER_ID, "Usage: /broadcast Your message here")
        return
    btext = parts[1]
    users = load_all_users()
    bot.send_message(OWNER_ID, f"📢 Broadcasting to {len(users)} users...")
    sent = 0
    failed = 0
    for uid in users:
        try:
            bot.send_message(uid, btext, parse_mode="HTML")
            sent += 1
            time.sleep(0.05)
        except:
            failed += 1
    bot.send_message(OWNER_ID, f"✅ Done. Sent: {sent}, Failed: {failed}")

# ======== Owner: Make redeem code ========
@bot.message_handler(commands=["makecode"])
def makecode_cmd(message):
    # Usage: /makecode <credits>
    if message.chat.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(OWNER_ID, "Usage: /makecode <credits>")
        return
    try:
        amt = int(parts[1])
        codes = load_redeem_codes()
        # generate unique code
        for _ in range(10):
            code = generate_code(8)
            if code not in codes:
                break
        else:
            # As fallback, append timestamp
            code = generate_code(6) + str(int(time.time()) % 1000)
        codes[code] = {
            "amount": int(amt),
            "used": False,
            "created_at": int(time.time())
        }
        save_redeem_codes(codes)
        bot.send_message(OWNER_ID, f"✅ Code created: <code>{code}</code> → {amt} credits", parse_mode="HTML")
    except Exception as e:
        bot.send_message(OWNER_ID, f"Error creating code: {e}")

# ======== User: Redeem code ========
@bot.message_handler(commands=["redeem"])
def redeem_cmd(message):
    uid = message.chat.id
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(uid, "Usage: /redeem <code>")
        return
    code = parts[1].strip().upper()
    try:
        codes = load_redeem_codes()
        if code not in codes:
            bot.send_message(uid, "❌ Invalid code.")
            return
        entry = codes[code]
        if entry.get("used"):
            bot.send_message(uid, "❌ This code has already been redeemed.")
            return
        # Mark used and add credits
        add_credits(uid, int(entry.get("amount", 0)))
        entry["used"] = True
        entry["redeemed_by"] = uid
        entry["redeemed_at"] = int(time.time())
        save_redeem_codes(codes)
        bot.send_message(uid, f"✅ Success! You've received {entry.get('amount')} credits.\nYour new balance: {get_credits(uid)}")
        # Notify owner (optional)
        try:
            bot.send_message(OWNER_ID, f"🔔 Code <code>{code}</code> redeemed by <b>{uid}</b> → {entry.get('amount')} credits", parse_mode="HTML")
        except:
            pass
    except Exception as e:
        bot.send_message(uid, f"Error redeeming code: {e}")

# ======== Fetch RC Info ========
@bot.message_handler(func=lambda m: True, content_types=['text'])
def fetch_rc_info(m):
    text = (m.text or "").strip()

    # FIX: Skip processing if the incoming message is a bot command (more reliable than startswith("/"))
    # Telegram marks commands in message.entities with type 'bot_command'
    if getattr(m, "entities", None):
        try:
            for ent in m.entities:
                if getattr(ent, "type", None) == "bot_command":
                    # It's a command; let command handlers handle it
                    return
        except:
            # if anything unexpected, fall back to previous startswith check
            if text.startswith("/"):
                return

    if text in ("🔍 Search RC", "ℹ️ About Bot", "👤 My Credit", "💳 Buy Credit"):
        if text == "🔍 Search RC":
            bot.send_message(m.chat.id, "Please enter the RC number (e.g., DL05AB1234):")
        elif text == "💳 Buy Credit":
            buy_credit(m)
        return

    user_id = m.chat.id

    if user_id != OWNER_ID and not all_channels_joined(user_id):
        ik = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            ik.add(types.InlineKeyboardButton(text=f"Join {ch}", url=f"https://t.me/{ch.lstrip('@')}"))
        ik.add(types.InlineKeyboardButton(text="I have joined ✅", callback_data="verify_join"))
        bot.send_message(user_id, "⚠️ You must join the required channels before using the bot.", reply_markup=ik)
        return

    if user_id != OWNER_ID:
        credits = get_credits(user_id)
        if credits <= 0:
            bot.send_message(
                user_id,
                "❌ You have no credits left.\n"
                "💳 Buy more credits here: @snxrajput\n"
                "Or share your referral link to earn free credits (/referral)."
            )
            return
        set_credits(user_id, credits - 1)

    rc_no = text.upper()
    if len(rc_no) < 4:
        bot.reply_to(m, "❌ Please send a valid RC number.")
        return

    bot.send_message(user_id, "⏳ Fetching details, please wait...")

    try:
        resp = requests.get(API_URL.format(rc_no), timeout=15)
        if resp.status_code != 200:
            if user_id != OWNER_ID:
                add_credits(user_id, 1)
            bot.send_message(user_id, f"❌ No data found for <code>{html.escape(rc_no)}</code>", parse_mode="HTML")
            return

        data = resp.json()
        if not data:
            if user_id != OWNER_ID:
                add_credits(user_id, 1)
            bot.send_message(user_id, f"❌ No data found for <code>{html.escape(rc_no)}</code>", parse_mode="HTML")
            return

        lines = []
        lines.append(f"🚗 <b>Vehicle Details</b>\n")
        lines.append(f"🔹 <b>RC Number:</b> <code>{html.escape(rc_no)}</code>\n")

        for key, value in data.items():
            display_key = html.escape(str(key))
            if isinstance(value, (dict, list)):
                try:
                    val_str = json.dumps(value, ensure_ascii=False)
                except:
                    val_str = str(value)
            else:
                val_str = str(value)

            val_str = val_str.strip()
            if val_str in ["", "None", "N/A"]:
                continue

            val_escaped = html.escape(val_str)
            if len(val_escaped) <= 40 and "\n" not in val_escaped:
                line = f"• <b>{display_key}:</b> {val_escaped}"
            else:
                line = f"• <b>{display_key}:</b>\n<pre>{val_escaped}</pre>"
            lines.append(line)

        final_msg = "\n".join(lines)
        bot.send_message(user_id, final_msg, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        if user_id != OWNER_ID:
            add_credits(user_id, 1)
        bot.send_message(user_id, f"⚠️ Error fetching data: {html.escape(str(e))}\nYour credit has been refunded.")

# ======== Run Bot ========
if __name__ == "__main__":
    ensure_files()
    print("🤖 Bot is running...")
    bot.infinity_polling()
