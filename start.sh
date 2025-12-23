#!/bin/bash

echo "🚀 بدء تشغيل بوت الأدعية والأذكار..."

# تحميل متغيرات البيئة
if [ -f .env ]; then
    export $(cat .env | xargs)
    echo "✅ تم تحميل متغيرات البيئة من .env"
else
    echo "⚠️ ملف .env غير موجود"
fi

# إنشاء مجلدات البيانات إذا لم تكن موجودة
mkdir -p data backups logs

# نسخ احتياطي للبيانات إن وجدت
if [ -f dua_bot.db ]; then
    cp dua_bot.db "backups/dua_bot_$(date +%Y%m%d_%H%M%S).db.backup"
    echo "✅ تم إنشاء نسخة احتياطية من قاعدة البيانات"
fi

# تثبيت المتطلبات إذا لزم الأمر
if [ -f requirements.txt ]; then
    pip install -r requirements.txt --upgrade
    echo "✅ تم تثبيت/تحديث المتطلبات"
fi

# التحقق من وجود توكن البوت
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ خطأ: TELEGRAM_BOT_TOKEN غير محدد"
    echo "يرجى تعيينه في متغيرات البيئة على Render"
    exit 1
fi

echo "✅ التوكن موجود، جاري تشغيل البوت..."
echo "📱 يمكنك الوصول للبوت على: https://t.me/$(python -c "import os; token=os.environ.get('TELEGRAM_BOT_TOKEN', ''); if token: print(token.split(':')[0])")bot"

# تشغيل البوت
exec python bot.py
