import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# ================== SETTINGS ==================
TOKEN = "8269653015:AAGybShdzQSmYMRcL860_iXyg4NSSKupYqg"
CHANNEL_USERNAME = "@AzkarChannel"   # قناة الاشتراك الإجباري
ADMINS = [5504483293]                 # ID الأدمن
# ==============================================

# ================== AZKAR ==================
MORNING_AZKAR = [
    "🌅 أصبحنا وأصبح الملك لله والحمد لله",
    "اللهم بك أصبحنا وبك أمسينا وبك نحيا وبك نموت",
    "رضيت بالله رباً وبالإسلام ديناً وبمحمد ﷺ نبياً",
    "اللهم إني أسألك خير هذا اليوم فتحه ونصره ونوره"
]

EVENING_AZKAR = [
    "🌙 أمسينا وأمسى الملك لله والحمد لله",
    "اللهم بك أمسينا وبك أصبحنا وبك نحيا وبك نموت",
    "أعوذ بكلمات الله التامات من شر ما خلق",
    "اللهم إني أسألك خير هذه الليلة فتحها ونصرها ونورها"
]
# ============================================

# ================= DATABASE =================
conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
conn.commit()

def add_user(user_id):
    cur.execute("INSERT OR IGNORE INTO users VALUES (?)", (user_id,))
    conn.commit()

def get_users():
    cur.execute("SELECT user_id FROM users")
    return [u[0] for u in cur.fetchall()]
# ============================================

# ================= CHECK SUB =================
async def is_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False
# ============================================

# ================= START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_subscribed(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="check")]
        ]
        await update.message.reply_text(
            "🚫 لا يمكنك استخدام البوت قبل الاشتراك في القناة",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    add_user(user_id)
    await update.message.reply_text(
        "🌿 مرحباً بك في بوت أذكار الصباح والمساء\n"
        "سيتم إرسال الأذكار تلقائيًا يومياً بإذن الله 🤍"
    )
# ============================================

# ================= CALLBACK ==================
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if await is_subscribed(context.bot, user_id):
        add_user(user_id)
        await query.edit_message_text("✅ تم التحقق بنجاح، مرحباً بك 🤍")
    else:
        await query.answer("❌ لم تشترك بعد", show_alert=True)
# ============================================

# ================= ADMIN =====================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return

    await update.message.reply_text(
        f"👮 لوحة الأدمن\n"
        f"👥 عدد المستخدمين: {len(get_users())}"
    )
# ============================================

# ================= SEND AZKAR ================
async def send_azkar(app, text):
    for user in get_users():
        try:
            await app.bot.send_message(user, text)
        except:
            pass

def morning_job(app):
    text = "🌅 أذكار الصباح\n\n" + "\n".join(MORNING_AZKAR)
    app.create_task(send_azkar(app, text))

def evening_job(app):
    text = "🌙 أذكار المساء\n\n" + "\n".join(EVENING_AZKAR)
    app.create_task(send_azkar(app, text))
# ============================================

# ================= MAIN ======================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(callback))

    scheduler = BackgroundScheduler()
    scheduler.add_job(morning_job, "cron", hour=6, minute=0, args=[app])
    scheduler.add_job(evening_job, "cron", hour=18, minute=0, args=[app])
    scheduler.start()

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
