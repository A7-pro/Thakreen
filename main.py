import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.background import BackgroundScheduler

# Bot Token
API_TOKEN = "7534795874:AAGehbCQR8h82qcNI1zabmFYdqg3satj4ag"
bot = telebot.TeleBot(API_TOKEN)

# Adhkar categories
adhkar_list = {
    "الصباح": ["اللهم بك أصبحنا وبك أمسينا...", "أصبحنا وأصبح الملك لله..."],
    "المساء": ["اللهم بك أمسينا وبك أصبحنا...", "أمسينا وأمسى الملك لله..."],
    "النوم": ["باسمك ربي وضعت جنبي...", "اللهم قني عذابك يوم تبعث عبادك..."],
    "الاستيقاظ": ["الحمد لله الذي أحيانا بعد ما أماتنا...", "لا إله إلا الله وحده لا شريك له..."],
    "بعد الصلاة": ["أستغفر الله... سبحان الله والحمد لله والله أكبر..."],
    "السفر": ["سبحان الذي سخر لنا هذا وما كنا له مقرنين..."]
}

# Initialize scheduler
scheduler = BackgroundScheduler()

# Store user preferences
user_preferences = {}

# Inline buttons for main menu
def main_menu_buttons():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📖 أذكار الصباح", callback_data="morning"))
    markup.add(InlineKeyboardButton("🌙 أذكار المساء", callback_data="evening"))
    markup.add(InlineKeyboardButton("🛌 أذكار النوم", callback_data="sleep"))
    markup.add(InlineKeyboardButton("🌅 أذكار الاستيقاظ", callback_data="wake"))
    markup.add(InlineKeyboardButton("📩 تواصل مع المطور", url="https://t.me/tahikal"))
    markup.add(InlineKeyboardButton("⏰ تخصيص التذكيرات", callback_data="schedule_reminder"))
    return markup

# Start command
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        "مرحبًا بك في بوت الأذكار! 🌟\n"
        "اختر ما يناسبك من الأذكار أو اضفني إلى مجموعتك.",
        reply_markup=main_menu_buttons()
    )

# Handle Adhkar callbacks
@bot.callback_query_handler(func=lambda call: call.data in ["morning", "evening", "sleep", "wake", "schedule_reminder"])
def handle_callbacks(call):
    if call.data in ["morning", "evening", "sleep", "wake"]:
        category = {
            "morning": "الصباح",
            "evening": "المساء",
            "sleep": "النوم",
            "wake": "الاستيقاظ"
        }[call.data]
        adhkar = adhkar_list[category]
        adhkar_text = "\n\n".join([f"🔹 {item}" for item in adhkar])
        bot.send_message(call.message.chat.id, f"📜 {category}:\n\n{adhkar_text}")
    elif call.data == "schedule_reminder":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("⏰ كل 6 ساعات", callback_data="6_hours"),
            InlineKeyboardButton("⏰ يومياً صباحاً", callback_data="daily_morning")
        )
        markup.add(InlineKeyboardButton("⏰ يومياً مساءً", callback_data="daily_evening"))
        bot.send_message(call.message.chat.id, "اختر الفترة الزمنية للتذكير:", reply_markup=markup)

# Schedule reminders
@bot.callback_query_handler(func=lambda call: call.data in ["6_hours", "daily_morning", "daily_evening"])
def schedule_reminders(call):
    user_id = call.message.chat.id
    if call.data == "6_hours":
        scheduler.add_job(send_reminder, "interval", hours=6, args=[user_id], id=f"6_hours_{user_id}", replace_existing=True)
        bot.send_message(user_id, "✅ سيتم تذكيرك بالأذكار كل 6 ساعات.")
    elif call.data == "daily_morning":
        scheduler.add_job(send_reminder, "cron", hour=6, minute=0, args=[user_id], id=f"morning_{user_id}", replace_existing=True)
        bot.send_message(user_id, "✅ سيتم تذكيرك بالأذكار كل صباح الساعة 6:00.")
    elif call.data == "daily_evening":
        scheduler.add_job(send_reminder, "cron", hour=18, minute=0, args=[user_id], id=f"evening_{user_id}", replace_existing=True)
        bot.send_message(user_id, "✅ سيتم تذكيرك بالأذكار كل مساء الساعة 6:00.")

def send_reminder(user_id):
    adhkar = adhkar_list["الصباح"]  # Default to morning Adhkar
    adhkar_text = "\n\n".join([f"🔹 {item}" for item in adhkar])
    bot.send_message(user_id, f"🔔 تذكير بالأذكار:\n\n{adhkar_text}")

# Run the bot and scheduler
if __name__ == "__main__":
    scheduler.start()
    print("Bot is running with scheduled reminders...")
    bot.polling()

# من خلال هذا الجزء سنضيف ميزة /addhelp التي تتيح فقط لك إضافة الأشخاص المصرح لهم بنشر الأذكار
# قم بإضافة هذا الجزء في الكود بعد أمر /start

AUTHORIZED_USERS = [7601607055]  # ضع هنا معرفك في تيليجرام فقط

@bot.message_handler(commands=["addhelp"])
def add_help(message):
    # تأكد أن المرسل هو فقط المطور
    if message.from_user.id in AUTHORIZED_USERS:
        bot.reply_to(message, "📝 من فضلك، أرسل اسم المستخدم الذي ترغب في إضافته لنشر الأذكار.")
        # هنا يمكنك إضافة الكود لجعل الشخص المصرح له ينشر الأذكار بعد ذلك
    else:
        bot.reply_to(message, "❌ فقط المطور يمكنه إضافة الأشخاص لنشر الأذكار.")
