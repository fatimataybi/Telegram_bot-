
import telebot
from telebot import types
from datetime import datetime
import os

# تسجيل التشغيل في ملف log
with open("log.txt", "a") as log:
    log.write(f"بوت بدأ في: {datetime.now()}
")

# قراءة التوكن من متغير البيئة
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

student_list = []
registration_open = True
group_id = None

def is_admin(message):
    try:
        member = bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("📥 سجل اسمي", "❌ احذف اسمي")
    keyboard.row("⏭ التالي")
    return keyboard

def format_list():
    if not student_list:
        return "📋 القائمة فارغة حالياً."
    return "\n".join([f"{i+1}. {name}" for i, name in enumerate(student_list)])

def show_list(chat_id):
    text = "🔴 قائمة طالبات أكاديمية الرحمة 🔴\n\n" + format_list()
    bot.send_message(chat_id, text, reply_markup=get_main_keyboard())

@bot.message_handler(commands=['start'])
def start(message):
    global group_id
    group_id = message.chat.id
    bot.send_message(message.chat.id, "👋 أهلاً بك في بوت القائمة الإلكترونية!")
    show_list(message.chat.id)

@bot.message_handler(commands=['stop'])
def stop_registration(message):
    global registration_open
    if is_admin(message):
        registration_open = False
        bot.reply_to(message, "🚫 تم إيقاف التسجيل مؤقتاً.")
    else:
        bot.reply_to(message, "❌ هذا الأمر مخصص للمشرفين فقط.")

@bot.message_handler(commands=['stopdefinitely'])
def reset_all(message):
    global student_list, registration_open
    if is_admin(message):
        student_list.clear()
        registration_open = True
        bot.reply_to(message, "🗑️ تم حذف جميع الأسماء وإعادة تفعيل التسجيل.")
        show_list(message.chat.id)
    else:
        bot.reply_to(message, "❌ هذا الأمر مخصص للمشرفين فقط.")

@bot.message_handler(func=lambda m: m.text == "📥 سجل اسمي")
def register_name(message):
    global registration_open
    if not registration_open:
        bot.reply_to(message, "🚫 التسجيل مغلق حالياً.")
        return

    username = message.from_user.first_name
    if message.from_user.username:
        username += f" (@{message.from_user.username})"
    name_with_tag = f"{username} #"

    if name_with_tag not in student_list:
        student_list.append(name_with_tag)
        bot.reply_to(message, f"✅ تم تسجيل اسمك.")
        show_list(message.chat.id)
    else:
        bot.reply_to(message, "⚠️ اسمك مسجل بالفعل.")

@bot.message_handler(func=lambda m: m.text == "❌ احذف اسمي")
def delete_name(message):
    username = message.from_user.first_name
    if message.from_user.username:
        username += f" (@{message.from_user.username})"
    name_with_tag = f"{username} #"

    if name_with_tag in student_list:
        student_list.remove(name_with_tag)
        bot.reply_to(message, "🗑️ تم حذف اسمك.")
        show_list(message.chat.id)
    else:
        bot.reply_to(message, "⚠️ اسمك غير موجود في القائمة.")

@bot.message_handler(func=lambda m: m.text == "⏭ التالي")
def next_name(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ هذا الزر مخصص للمشرفين فقط.")
        return

    if student_list:
        name = student_list.pop(0)
        bot.send_message(message.chat.id, f"🎯 التالي:\n{name}")
        show_list(message.chat.id)
    else:
        bot.send_message(message.chat.id, "📭 القائمة فارغة.")

print("🤖 el bot está funcionando...")
bot.infinity_polling()
