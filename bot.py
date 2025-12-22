import os
import random
import sqlite3
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== CONFIG =====
TOKEN = os.getenv("8269653015:AAGybShdzQSmYMRcL860_iXyg4NSSKupYqg")
ADMIN_ID = 5504483293

# ===== DATABASE =====
conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    subscribed INTEGER DEFAULT 1
)
""")
conn.commit()

def add_user(chat_id):
    cur.execute(
        "INSERT OR IGNORE INTO users (chat_id, subscribed) VALUES (?,1)",
        (chat_id,)
    )
    conn.commit()

def subscribe(chat_id):
    cur.execute("UPDATE users SET subscribed=1 WHERE chat_id=?", (chat_id,))
    conn.commit()

def unsubscribe(chat_id):
    cur.execute("UPDATE users SET subscribed=0 WHERE chat_id=?", (chat_id,))
    conn.commit()

def get_subscribed_users():
    cur.execute("SELECT chat_id FROM users WHERE subscribed=1")
    return [u[0] for u in cur.fetchall()]

# ===== DATA =====
azkar = [
    "سبحان الله",
    "الحمد لله",
    "لا إله إلا الله",
    "الله أكبر",
    "لا حول ولا قوة إلا بالله"
]

# ===== API =====
def get_ayah():
    r = requests.get("https://api.alquran.cloud/v1/ayah/random/ar", timeout=10)
    d = r.json()["data"]
    return f"📖 {d['text']}\n\n({d['surah']['name']})"

def get_hadith():
    r = requests.get("https://api.hadith.gading.dev/books/muslim?range=1-300", timeout=10)
    h = random.choice(r.json()["data"]["hadiths"])
    return f"📜 {h['arab']}"

# ===== KEYBOARD =====
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📿 ذكر", callback_data="zekr")],
        [InlineKeyboardButton("📖 آية", callback_data="ayah")],
        [InlineKeyboardButton("📜 حديث", callback_data="hadith")],
        [
            InlineKeyboardButton("🔔 اشتراك", callback_data="sub"),
            InlineKeyboardButton("🔕 إلغاء", callback_data="unsub")
        ]
    ])

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_chat.id)
    await update.message.reply_text(
        "🕌 مرحبًا بك في بوت الأذكار",
        reply_markup=main_keyboard()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "zekr":
        text = random.choice(azkar)
    elif query.data == "ayah":
        text = get_ayah()
    elif query.data == "hadith":
        text = get_hadith()
    elif query.data == "sub":
        subscribe(query.message.chat.id)
        text = "✅ تم تفعيل الاشتراك"
    elif query.data == "unsub":
        unsubscribe(query.message.chat.id)
        text = "❌ تم إلغاء الاشتراك"

    await query.edit_message_text(text, reply_markup=main_keyboard())

# ===== AUTO ZEKR =====
async def hourly_zekr(context: ContextTypes.DEFAULT_TYPE):
    zekr = random.choice(azkar)
    for user in get_subscribed_users():
        try:
            await context.bot.send_message(user, f"⏰ {zekr}")
        except:
            pass

# ===== RUN =====
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

app.job_queue.run_repeating(hourly_zekr, interval=3600, first=30)

print("Bot is running...")
app.run_polling()
