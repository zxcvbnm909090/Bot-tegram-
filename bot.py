#!/usr/bin/env python3
"""
بوت تليجرام للأدعية والأذكار
مطور خصيصاً لـ Render.com
"""

import os
import logging
import sys
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from database import Database
from utils import DataLoader, TimeUtils

# إعدادات Flask لـ Render
app = Flask(__name__)

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# تهيئة الكائنات
db = Database()
data_loader = DataLoader()
time_utils = TimeUtils()

# الحصول على التوكن من متغيرات Render
TOKEN = os.environ.get("8007893522:AAHAXReG3KRDzJDYORSRAcEV5a5Z7rAIZrI", "")
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL", "") + "/webhook"

if not TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN غير محدد!")
    logger.info("⚙️ يرجى تعيينه في Environment Variables على Render")
    sys.exit(1)

# إنشاء تطبيق البوت
application = Application.builder().token(TOKEN).build()

# وظائف البوت (نفس الوظائف السابقة مع تعديلات بسيطة)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب"""
    try:
        user = update.effective_user
        db.add_user(user.id, user.username, user.first_name, user.last_name)
        
        greeting = time_utils.get_greeting()
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("أذكار الصباح 🌅", callback_data="morning")],
            [InlineKeyboardButton("أذكار المساء 🌙", callback_data="evening")],
            [InlineKeyboardButton("أدعية متنوعة 📖", callback_data="duas")],
            [InlineKeyboardButton("الأدعية المفضلة ⭐", callback_data="favorites")],
            [InlineKeyboardButton("إحصائياتي 📊", callback_data="stats")],
            [InlineKeyboardButton("المساعدة ❓", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
        {greeting} {user.first_name} 👋
        
        *مرحباً بك في بوت الأدعية والأذكار*
        
        🤖 *مميزات البوت:*
        • أذكار الصباح والمساء
        • أدعية متنوعة من القرآن والسنة
        • حفظ الأدعية المفضلة
        • إحصائيات وتتبع
        • تذكيرات تلقائية
        
        استخدم /help للمساعدة
        
        ⚡ *البوت مستضاف على:* Render.com
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        logger.info(f"👤 مستخدم جديد: {user.id} - {user.first_name}")
        
    except Exception as e:
        logger.error(f"❌ خطأ في start: {e}")
        await update.message.reply_text("حدث خطأ، يرجى المحاولة لاحقاً.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعليمات استخدام البوت"""
    help_text = """
    *📚 تعليمات استخدام البوت:*
    
    *الأوامر المتاحة:*
    /start - بدء البوت وعرض القائمة الرئيسية
    /help - عرض هذه التعليمات
    /morning - أذكار الصباح
    /evening - أذكار المساء
    /random - دعاء عشوائي
    /stats - إحصائياتك اليومية
    /favorites - الأدعية المفضلة
    
    *كيفية الاستخدام:*
    1. اضغط على /start لبدء البوت
    2. اختر من القائمة المنسدلة
    3. استخدم الأزرار للتنقل
    4. أضف الأدعية للمفضلة
    
    *معلومات تقنية:*
    🤖 الإصدار: 2.0
    🚀 الاستضافة: Render.com
    🔄 التحديث: تلقائي
    
    للمساعدة: اضغط على زر المساعدة في القائمة
    """
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإحصائيات"""
    user_id = update.effective_user.id
    stats = db.get_daily_stats(user_id)
    
    if stats:
        morning, evening, prayer, dua = stats
        total = morning + evening + prayer + dua
        
        text = f"""
        📊 *إحصائياتك اليومية:*
        
        🌅 أذكار الصباح: {morning}
        🌙 أذكار المساء: {evening}
        🕌 أذكار الصلاة: {prayer}
        📖 أدعية متنوعة: {dua}
        
        *المجموع:* {total} ذكراً
        
        🎯 *هدف اليوم:* {max(50 - total, 0)} ذكراً متبقياً
        📈 *إنجاز:* {min(total, 50)}/50
        
        استمر في الذكر، فالذكر يرفع الدرجات ويحط الخطايا 🙏
        """
    else:
        text = "📊 لم تقم بقراءة أي أذكار اليوم. ابدأ الآن! 🌟"
    
    await update.message.reply_text(text, parse_mode="Markdown")

# إضافة handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("stats", stats_command))
application.add_handler(CommandHandler("morning", start))
application.add_handler(CommandHandler("evening", start))
application.add_handler(CommandHandler("random", start))
application.add_handler(CommandHandler("favorites", start))

# إضافة handler للأزرار
from telegram.ext import CallbackQueryHandler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "morning":
        morning_data = data_loader.load_morning()
        if morning_data["items"]:
            item = morning_data["items"][0]
            await query.edit_message_text(
                f"*{item['text']}*\n\n📚 المرجع: {item['reference']}",
                parse_mode="Markdown"
            )
    elif query.data == "stats":
        await stats_command(update, context)
    elif query.data == "help":
        await help_command(update, context)

application.add_handler(CallbackQueryHandler(button_handler))

# معالج الأخطاء
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"حدث خطأ: {context.error}")
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ حدث خطأ. جاري إصلاحه..."
        )
    except:
        pass

application.add_error_handler(error_handler)

# صفحة الصحة للتحقق
@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "dua-bot-telegram"}

# صفحة الرئيسية
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>بوت الأدعية والأذكار</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 50px;
                margin: 0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 20px;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature {
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 10px;
            }
            .button {
                display: inline-block;
                background: white;
                color: #667eea;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 50px;
                font-weight: bold;
                margin: 20px;
                transition: transform 0.3s;
            }
            .button:hover {
                transform: scale(1.05);
            }
            .stats {
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 بوت الأدعية والأذكار</h1>
            <p>بوت تليجرام متكامل للأدعية والأذكار اليومية</p>
            
            <div class="features">
                <div class="feature">🌅 أذكار الصباح</div>
                <div class="feature">🌙 أذكار المساء</div>
                <div class="feature">📖 أدعية متنوعة</div>
                <div class="feature">⭐ حفظ المفضلة</div>
                <div class="feature">📊 إحصائيات</div>
                <div class="feature">🔔 تذكيرات</div>
            </div>
            
            <a href="https://t.me/{}bot" class="button" target="_blank">
                🔗 استخدام البوت على تليجرام
            </a>
            
            <div class="stats">
                <h3>📈 إحصائيات البوت</h3>
                <p>👥 عدد المستخدمين: {}</p>
                <p>📅 الأذكار اليوم: {}</p>
                <p>🚀 الحالة: {} ✅</p>
            </div>
            
            <p style="margin-top: 30px; font-size: 0.9em;">
                ⚡ مستضاف على Render.com | 🔄 يتم التحديث تلقائياً
            </p>
        </div>
    </body>
    </html>
    """.format(
        TOKEN.split(':')[0] if TOKEN else "your_bot",
        db.get_total_users(),
        sum(db.get_daily_stats(123)[:4]) if db.get_daily_stats(123) else 0,
        "نشط"
    )

# ويب هوك لـ Render
@app.route('/webhook', methods=['POST'])
def webhook():
    """معالجة الويب هوك من تليجرام"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return 'OK'

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """تعيين الويب هوك"""
    if not WEBHOOK_URL:
        return "❌ WEBHOOK_URL غير محدد", 400
    
    try:
        # استخدام application.bot مباشرة
        success = application.bot.set_webhook(WEBHOOK_URL)
        if success:
            logger.info(f"✅ تم تعيين الويب هوك: {WEBHOOK_URL}")
            return f"✅ تم تعيين الويب هوك: {WEBHOOK_URL}"
        else:
            logger.error("❌ فشل تعيين الويب هوك")
            return "❌ فشل تعيين الويب هوك", 500
    except Exception as e:
        logger.error(f"❌ خطأ في تعيين الويب هوك: {e}")
        return f"❌ خطأ: {e}", 500

def main():
    """الدالة الرئيسية للتشغيل"""
    try:
        # تشغيل Flask
        port = int(os.environ.get("PORT", 10000))
        
        # تعيين الويب هوك إذا كان هناك URL
        if WEBHOOK_URL and "http" in WEBHOOK_URL:
            logger.info(f"🚀 جاري تعيين الويب هوك: {WEBHOOK_URL}")
            application.bot.set_webhook(WEBHOOK_URL)
            logger.info("✅ تم تعيين الويب هوك بنجاح")
            
            # تشغيل Flask فقط (الويب هوك)
            app.run(host='0.0.0.0', port=port, debug=False)
        else:
            # وضع Polling (للتطوير)
            logger.info("🔧 وضع التطوير (Polling)")
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
    except Exception as e:
        logger.error(f"❌ خطأ في التشغيل: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
