from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import requests, random, sqlite3
from datetime import time

# ====== CONFIG ======
TOKEN = "8269653015:AAGybShdzQSmYMRcL860_iXyg4NSSKupYqg"
ADMIN_ID = 5504483293
CHANNEL_USERNAME = "@YourChannelName"

# ====== DATABASE ======
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
    cur.execute("INSERT OR IGNORE INTO users (chat_id, subscribed) VALUES (?,1)", (chat_id,))
    conn.commit()

def subscribe(chat_id):
    cur.execute("UPDATE users SET subscribed=1 WHERE chat_id=?", (chat_id,))
    conn.commit()

def unsubscribe(chat_id):
    cur.execute("UPDATE users SET subscribed=0 WHERE chat_id=?", (chat_id,))
    conn.commit()

def get_users(subscribed_only=False):
    if subscribed_only:
        cur.execute("SELECT chat_id FROM users WHERE subscribed=1")
    else:
        cur.execute("SELECT chat_id FROM users")
    return [u[0] for u in cur.fetchall()]

# ====== DATA ======
azkar = [
    "سبحان الله",
    "الحمد لله",
    "لا إله إلا الله",
    "الله أكبر",
    "لا حول ولا قوة إلا بالله"
]

morning_azkar = [
    "أصبحنا وأصبح الملك لله",
    "اللهم بك أصبحنا وبك أمسينا",
    "رضيت بالله ربًا وبالإسلام دينًا وبمحمد ﷺ نبيًا"
]

evening_azkar = [
    "أمسينا وأمسى الملك لله",
    "اللهم بك أمسينا وبك أصبحنا",
    "أعوذ بكلمات الله التامات من شر ما خلق"
]

# ====== API ======
def get_ayah():
    r = requests.get("https://api.alquran.cloud/v1/ayah/random/ar", timeout=10)
    d = r.json()["data"]
    return f"📖 {d['text']}\n\n({d['surah']['name']})"

def get_hadith():
    r = requests.get("https://api.hadith.gading.dev/books/muslim?range=1-300", timeout=10)
    h = random.choice(r.json()["data"]["hadiths"])
    return f"📜 {h['arab']}"

# ====== KEYBOARD ======
def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📿 ذكر", callback_data="zekr")],
        [InlineKeyboardButton("📖 آية", callback_data="ayah")],
        [InlineKeyboardButton("📜 حديث", callback_data="hadith")],
        [
            InlineKeyboardButton("🔔 اشتراك", callback_data="sub"),
            InlineKeyboardButton("🔕 إلغاء", callback_data="unsub")
        ]
    ])

# ====== COMMANDS ======
async def start(update, context):
    add_user(update.effective_chat.id)
    await update.message.reply_text(
        "🕌 *البوت الإسلامي*\nاختر من الأزرار:",
        reply_markup=keyboard(),
        parse_mode="Markdown"
    )

async def buttons(update, context):
    q = update.callback_query
    await q.answer()

    if q.data == "zekr":
        text = random.choice(azkar)
    elif q.data == "ayah":
        text = get_ayah()
    elif q.data == "hadith":
        text = get_hadith()
    elif q.data == "sub":
        subscribe(q.message.chat.id)
        text = "✅ تم تفعيل الاشتراك"
    elif q.data == "unsub":
        unsubscribe(q.message.chat.id)
        text = "❌ تم إلغاء الاشتراك"

    await q.edit_message_text(text, reply_markup=keyboard())

# ====== CHANNEL ======
async def post_to_channel(context, text):
    try:
        await context.bot.send_message(CHANNEL_USERNAME, text)
    except:
        pass

# ====== AUTO TASKS ======
async def hourly_zekr(context):
    zekr = random.choice(azkar)
    for u in get_users(subscribed_only=True):
        try:
            await context.bot.send_message(u, f"⏰ {zekr}")
        except:
            pass
    await post_to_channel(context, f"📿 {zekr}")

async def morning(context):
    msg = random.choice(morning_azkar)
    for u in get_users(subscribed_only=True):
        try:
            await context.bot.send_message(u, "🌅 " + msg)
        except:
            pass
    await post_to_channel(context, "🌅 " + msg)

async def evening(context):
    msg = random.choice(evening_azkar)
    for u in get_users(subscribed_only=True):
        try:
            await context.bot.send_message(u, "🌙 " + msg)
        except:
            pass
    await post_to_channel(context, "🌙 " + msg)

# ====== ADMIN ======
def is_admin(update):
    return update.effective_chat.id == ADMIN_ID

async def admin(update, context):
    if not is_admin(update):
        return
    await update.message.reply_text(
        "🛡️ لوحة الأدمن\n"
        "/stats\n"
        "/broadcast رسالة\n"
        "/sendzekr"
    )

async def stats(update, context):
    if is_admin(update):
        await update.message.reply_text(f"👥 المستخدمون: {len(get_users())}")

async def broadcast(update, context):
    if not is_admin(update) or not context.args:
        return
    msg = " ".join(context.args)
    for u in get_users():
        try:
            await context.bot.send_message(u, f"📢 {msg}")
        except:
            pass

async def sendzekr(update, context):
    if not is_admin(update):
        return
    for u in get_users():
        try:
            await context.bot.send_message(u, f"📿 {random.choice(azkar)}")
        except:
            pass

# ====== RUN ======
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("sendzekr", sendzekr))

app.job_queue.run_repeating(hourly_zekr, interval=3600, first=10)
app.job_queue.run_daily(morning, time=time(6, 0))
app.job_queue.run_daily(evening, time=time(18, 0))

app.run_polling()
