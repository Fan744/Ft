import telebot
import requests
import json
import os

# === BOT TOKEN ===
BOT_TOKEN = "8369100760:AAEEkuwbZz0eOghLboKeP1qN2l9tJd0OdwE"
bot = telebot.TeleBot(BOT_TOKEN)

# === ADMIN USER ID ===
ADMIN_ID = UR_ID  # replace with your Telegram ID

# === USERS FILE ===
USERS_FILE = "users.json"

# === LOAD USERS ===
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# === SAVE FUNCTION ===
def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# === COMMAND: /start ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    args = message.text.split()

    if user_id not in users:
        users[user_id] = {
            "balance": 500,
            "referrals": 0,
            "referred_by": None,
            "banned": False,
            "premium": False
        }

        # Referral logic
        if len(args) > 1:
            referrer_id = args[1]
            if referrer_id in users and referrer_id != user_id:
                users[referrer_id]["balance"] += 500
                users[referrer_id]["referrals"] += 1
                users[user_id]["referred_by"] = referrer_id
                bot.send_message(
                    int(referrer_id),
                    f"🎉 You earned ₹500 for referring a new user!\nCurrent balance: ₹{users[referrer_id]['balance']}"
                )

                # Premium condition
                if users[referrer_id]["referrals"] >= 5:
                    users[referrer_id]["premium"] = True
                    bot.send_message(
                        int(referrer_id),
                        "🌟 Congratulations! You are now a **LIFETIME PREMIUM USER!**"
                    )

        save_users()
        bot.reply_to(message, "🎉 Welcome to R4MODS Bot!\nYou got ₹500 starting balance.")
    else:
        bot.reply_to(message, "👋 Welcome back!")

    # === FIXED REFERRAL LINK ===
    bot_info = bot.get_me()
    bot_username = bot_info.username
    if bot_username:
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
    else:
        ref_link = f"https://t.me/{bot_info.id}?start={user_id}"

    bal = users[user_id]["balance"]
    premium_status = "✅ Premium User" if users[user_id]["premium"] else "❌ Normal User"

    welcome_text = (
        "```\n"
        "✦═━─━═✧ WELCOME TO R4MODS BOT ✦═━─━═✦\n\n"
        "REFER YOUR 5 FRIENDS TO BECOME LIFE TIME PREMIUM USER 💎\n\n"
        f"💰 Balance: ₹{bal}\n"
        f"👑 Status: {premium_status}\n\n"
        "🔗 Referral Link:\n"
        f"`{ref_link}`\n\n"
        "✦═━─━═✧ R4MODS ✧═━─━═✦\n"
        "BOT BY - @its_mahesh_ms\nCHANNEL - @R4MODS\n"
        "✦═━─━═✧ R4MODS ✧═━─━═✦"
        "\n```"
    )

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text="📋 Copy Referral Link", url=ref_link))
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

    if message.from_user.id == ADMIN_ID:
        admin_text = (
            "```\n"
            "⚙️ ADMIN COMMANDS:\n"
            "/addcredit <user_id> <amount>\n"
            "/removecredit <user_id> <amount>\n"
            "/ban <user_id>\n"
            "/unban <user_id>\n"
            "/premium <user_id>\n"
            "/unpremium <user_id>\n"
            "/broadcast <message>\n"
            "/users  ← show total users\n"
            "```"
        )
        bot.send_message(message.chat.id, admin_text, parse_mode="Markdown")


# === ADMIN COMMANDS ===
@bot.message_handler(commands=['addcredit'])
def add_credit(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid, amount = message.text.split()
        amount = int(amount)
        if uid in users:
            users[uid]["balance"] += amount
            save_users()
            bot.reply_to(message, f"```✅ Added ₹{amount} to user {uid}```", parse_mode="Markdown")
        else:
            bot.reply_to(message, "```❌ User not found.```", parse_mode="Markdown")
    except:
        bot.reply_to(message, "```⚠️ Usage: /addcredit <user_id> <amount>```", parse_mode="Markdown")


@bot.message_handler(commands=['removecredit'])
def remove_credit(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid, amount = message.text.split()
        amount = int(amount)
        if uid in users:
            users[uid]["balance"] -= amount
            save_users()
            bot.reply_to(message, f"```✅ Removed ₹{amount} from user {uid}```", parse_mode="Markdown")
        else:
            bot.reply_to(message, "```❌ User not found.```", parse_mode="Markdown")
    except:
        bot.reply_to(message, "```⚠️ Usage: /removecredit <user_id> <amount>```", parse_mode="Markdown")


@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        if uid in users:
            users[uid]["banned"] = True
            save_users()
            bot.reply_to(message, f"```🚫 User {uid} banned.```", parse_mode="Markdown")
        else:
            bot.reply_to(message, "```❌ User not found.```", parse_mode="Markdown")
    except:
        bot.reply_to(message, "```⚠️ Usage: /ban <user_id>```", parse_mode="Markdown")


@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        if uid in users:
            users[uid]["banned"] = False
            save_users()
            bot.reply_to(message, f"```✅ User {uid} unbanned.```", parse_mode="Markdown")
        else:
            bot.reply_to(message, "```❌ User not found.```", parse_mode="Markdown")
    except:
        bot.reply_to(message, "```⚠️ Usage: /unban <user_id>```", parse_mode="Markdown")


@bot.message_handler(commands=['premium'])
def premium_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        if uid in users:
            users[uid]["premium"] = True
            save_users()
            bot.reply_to(message, f"```🌟 User {uid} upgraded to Premium.```", parse_mode="Markdown")
        else:
            bot.reply_to(message, "```❌ User not found.```", parse_mode="Markdown")
    except:
        bot.reply_to(message, "```⚠️ Usage: /premium <user_id>```", parse_mode="Markdown")


@bot.message_handler(commands=['unpremium'])
def unpremium_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid = message.text.split()
        if uid in users:
            users[uid]["premium"] = False
            save_users()
            bot.reply_to(message, f"```❌ User {uid} downgraded from Premium.```", parse_mode="Markdown")
        else:
            bot.reply_to(message, "```❌ User not found.```", parse_mode="Markdown")
    except:
        bot.reply_to(message, "```⚠️ Usage: /unpremium <user_id>```", parse_mode="Markdown")


@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        text = message.text.split(" ", 1)[1]
    except IndexError:
        bot.reply_to(message, "```⚠️ Usage: /broadcast <message>```", parse_mode="Markdown")
        return
    sent, failed = 0, 0
    for uid in users:
        try:
            bot.send_message(int(uid), f"```\n{text}\n```", parse_mode="Markdown")
            sent += 1
        except:
            failed += 1
    bot.reply_to(message, f"```✅ Broadcast done!\nSent: {sent}\nFailed: {failed}```", parse_mode="Markdown")


# === NEW ADMIN COMMAND: /users ===
@bot.message_handler(commands=['users'])
def users_count(message):
    if message.from_user.id != ADMIN_ID:
        return
    total_users = len(users)
    premium_users = sum(1 for u in users.values() if u.get("premium"))
    banned_users = sum(1 for u in users.values() if u.get("banned"))
    

# === MAIN FEATURE ===
@bot.message_handler(func=lambda message: True)
def get_info(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        bot.reply_to(message, "```❌ Please use /start first.```", parse_mode="Markdown")
        return

    if users[user_id].get("banned"):
        bot.reply_to(message, "```🚫 You are banned from using this bot.```", parse_mode="Markdown")
        return

    number = message.text.strip()
    if not number.isdigit() or len(number) < 10:
        bot.reply_to(message, "```❌ Please send a valid 10-digit number.```", parse_mode="Markdown")
        return

    if not users[user_id]["premium"] and users[user_id]["balance"] < 5:
        bot.reply_to(message, "```💸 Insufficient balance! Each search costs ₹5.\nInvite 5 friends to get lifetime premium access!```", parse_mode="Markdown")
        return

    if not users[user_id]["premium"]:
        users[user_id]["balance"] -= 5
        save_users()

    # === UPDATED API ===
    api_url = f"UR_API_HERE"

    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            try:
                data = response.json()
                formatted = json.dumps(data, indent=2, ensure_ascii=False)
                reply_msg = (
                    f"```\n{formatted}\n```\n"
                    f"💰 {'No charge (Premium User)' if users[user_id]['premium'] else '-₹5 deducted'}\n"
                    f"Remaining balance: ₹{users[user_id]['balance']}\n\n"
                    "```\n✦═━─━═✧ R4MODS ✧═━─━═✦\n"
                    "BOT BY - @its_mahesh_ms \nCHANNEL - @R4MODS \n✦═━─━═✧ R4MODS ✧═━─━═✦```"
                )
                bot.reply_to(message, reply_msg, parse_mode="Markdown")
            except:
                bot.reply_to(message, "```⚠️ Unable to parse JSON.\nTry another number.```", parse_mode="Markdown")
        else:
            bot.reply_to(message, "```⚠️ API not responding properly.```", parse_mode="Markdown")
    except requests.exceptions.RequestException:
        bot.reply_to(message, "```⚠️ Error connecting to API.```", parse_mode="Markdown")


# === START BOT ===
print("🤖 Bot running with wallet + referral + premium + admin panel system...")
bot.infinity_polling()
