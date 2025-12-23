# 🤖 بوت الأدعية والأذكار - Render.com

[![نشر على Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/dua-bot)

بوت تليجرام متكامل للأدعية والأذكار، مستضاف على Render.com.

## ✨ الميزات
- أذكار الصباح والمساء
- أدعية متنوعة من القرآن والسنة
- حفظ الأدعية المفضلة
- إحصائيات يومية
- واجهة ويب للتحكم
- تحديث تلقائي

## 🚀 النشر على Render

### الطريقة 1: زر النشر السريع (مستحسن)
[![نشر على Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/dua-bot)

### الطريقة 2: يدوياً
1. سجل الدخول إلى [Render.com](https://render.com)
2. اضغط على **New +** → **Web Service**
3. صل بحساب GitHub أو GitLab
4. اختر مستودع البوت
5. املأ المعلومات:
   - **Name:** `dua-bot` (أو أي اسم تريده)
   - **Environment:** `Python 3`
   - **Region:** `Frankfurt` (أو أقرب region لك)
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
6. اضغط على **Advanced** وأضف Environment Variables:
   - `TELEGRAM_BOT_TOKEN`: توكن بوتك من @BotFather
7. اضغط **Create Web Service**

## ⚙️ إعداد البوت

### 1. الحصول على توكن البوت
1. افتح تليجرام وابحث عن `@BotFather`
2. أرسل `/newbot`
3. اتبع التعليمات واحفظ التوكن

### 2. إضافة Environment Variables على Render
في لوحة تحكم Render:
1. اذهب إلى خدمة البوت
2. اضغط على **Environment**
3. أضف المتغيرات:
