import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.background import BackgroundScheduler

# Bot Token
API_TOKEN = "7534795874:AAGehbCQR8h82qcNI1zabmFYdqg3satj4ag"
bot = telebot.TeleBot(API_TOKEN)

# معرف المستخدم الذي يمكنه إدارة البوت
AUTHORIZED_USER = 7601607055  # معرف المطور

# روابط الصور الخاصة بالأذكار
adhkar_images = {
    "الصباح": [
        "https://pbs.twimg.com/media/GfVf18cXsAAZFFl?format=jpg&name=large"  # أذكار الصباح
    ],
    "المساء": [
        "https://pbs.twimg.com/media/GfVf18cXkAM88X2?format=jpg&name=large"  # أذكار المساء
    ],
    "النوم": [
        "https://pbs.twimg.com/media/GfVf18cWEAAxdXy?format=jpg&name=large"  # أذكار النوم
    ],
}

# إرسال الأذكار كصور من الروابط
def send_adhkar_as_image(chat_id, category):
    for image_url in adhkar_images.get(category, []):
        bot.send_photo(chat_id, image_url)

# إرسال الأذكار بناءً على الفئة
@bot.message_handler(commands=['morning', 'evening', 'sleep'])
def send_adhkar(message):
    category = message.text[1:]  # استخراج الفئة من الأمر (morning, evening, sleep)
    if category in adhkar_images:
        send_adhkar_as_image(message.chat.id, category)
    else:
        bot.send_message(message.chat.id, "❌ فئة الأذكار غير صحيحة.")

# تفاعل مع الأزرار (Inline buttons) في لوحة التحكم
def send_admin_panel(message):
    keyboard = InlineKeyboardMarkup(row_width=2)

    # إضافة الأزرار في لوحة التحكم
    buttons = [
        InlineKeyboardButton("أذكار الصباح", callback_data="morning"),
        InlineKeyboardButton("أذكار المساء", callback_data="evening"),
        InlineKeyboardButton("أذكار النوم", callback_data="sleep"),
    ]
    keyboard.add(*buttons)

    bot.send_message(
        message.chat.id,
        "مرحبًا في لوحة التحكم! اختر الأذكار التي ترغب في تلقيها:",
        reply_markup=keyboard
    )

# عندما يتم الضغط على زر من الأزرار
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.from_user.id == AUTHORIZED_USER:
        category = call.data  # الحصول على الفئة (morning, evening, sleep)
        if category in adhkar_images:
            send_adhkar_as_image(call.message.chat.id, category)
        else:
            bot.send_message(call.message.chat.id, "❌ فئة الأذكار غير صحيحة.")
    else:
        bot.send_message(call.message.chat.id, "❌ أنت لست الشخص المصرح له.")

# إضافة أمر /admin للوصول إلى لوحة التحكم
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == AUTHORIZED_USER:
        send_admin_panel(message)  # إرسال لوحة التحكم عند استخدام أمر /admin
    else:
        bot.send_message(message.chat.id, "❌ أنت لست الشخص المصرح له.")

# إضافة شخص
@bot.message_handler(commands=['addhelp'])
def add_help(message):
    if message.from_user.id == AUTHORIZED_USER:
        user_id = int(message.text.split()[1])
        bot.send_message(message.chat.id, f"✅ تم إضافة {user_id} لنشر الأذكار.")
    else:
        bot.send_message(message.chat.id, "❌ أنت لست الشخص المصرح له.")

# إرسال الأذكار عبر لوحة التحكم
@bot.message_handler(commands=['sendadhkar'])
def send_adhkar(message):
    if message.from_user.id == AUTHORIZED_USER:
        category = "الصباح"  # تحديد الفئة
        send_adhkar_as_image(message.chat.id, category)
        bot.reply_to(message, "✅ تم إرسال الأذكار.")
    else:
        bot.reply_to(message, "❌ أنت لست الشخص المصرح له.")

# تغيير ترحيب البوت
@bot.message_handler(commands=['changewelcome'])
def change_welcome(message):
    if message.from_user.id == AUTHORIZED_USER:
        new_welcome = message.text.split(" ", 1)[1]
        bot.send_message(message.chat.id, f"✅ تم تغيير الترحيب إلى: {new_welcome}")
    else:
        bot.reply_to(message, "❌ أنت لست الشخص المصرح له.")

# تعطيل أو تفعيل البوت
@bot.message_handler(commands=['togglebot'])
def toggle_bot(message):
    if message.from_user.id == AUTHORIZED_USER:
        bot.send_message(message.chat.id, "✅ تم تعطيل أو تفعيل البوت.")
    else:
        bot.reply_to(message, "❌ أنت لست الشخص المصرح له.")

# تشغيل البوت
if __name__ == "__main__":
    # جدولة الأذكار اليومية
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_adhkar, 'cron', hour=6, minute=0)  # وقت الإرسال يوميًا الساعة 6 صباحًا
    scheduler.start()

    bot.polling()
if __name__ == "__main__":
    bot.polling(none_stop=True)

