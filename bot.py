import telebot
from telebot import types
import os
import threading
import time
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")  # أو ضعي التوكن مباشرة بين "" لو مو مستعملة متغير بيئة
bot = telebot.TeleBot(TOKEN)

default_tasks = [
    "☀️ صلاة الفجر 🧎‍♂️", "اذكار بعد صلاة الفجر 📕", "الدعاء بعد صلاة الفجر 🤲", "اذكار الصباح",
    "🧎‍♂️ صلاة الضحى 🧎‍♂️", "الدعاء بعد صلاة الضحى 🤲", "الرقية الشرعية 🙏", "صلاة الظهر فرض وسنة",
    "📖 اذكار بعد صلاة الظهر 📕", "الدعاء بعد صلاة الظهر 🤲", "نصف جزء من القرآن ",
    "📕 استغفار وتسبيح وتهليل وتكبير بشكل كبير", "صلاة العصر 🧎‍♂️", "اذكار بعد صلاة العصر",
    "📕 الدعاء بعد صلاة العصر 🤲", "اذكار المساء 🌙", "صلاة المغرب والسنة 🧎‍♂️", "اذكار بعد صلاة المغرب",
    "📕 الدعاء بعد صلاة المغرب 🤲", "صلاة العشاء والسنة والشفع والوتر 🧎‍♂️", "اذكار بعد صلاة العشاء",
    "🧎‍♂️ الدعاء بعد صلاة العشاء 🤲", "صلاة القيام على الأقل 2+ ركعات",
    ,"📿 أستغفار/تسبيح/تهليل/تكبير بشكل كبير",
   " الدعاء 🤲"
]

user_tasks = {}

def generate_task_keyboard(user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    tasks = user_tasks.get(user_id, default_tasks.copy())
    buttons = []
    for i, task in enumerate(tasks):
        if task.startswith("✅"):
            continue  # لا نضيف المهام المنجزة
        button = types.InlineKeyboardButton(text=task, callback_data=f"done_{i}")
        buttons.append(button)
    markup.add(*buttons)
    return markup

def get_task_progress_text(user_id):
    tasks = user_tasks.get(user_id, default_tasks.copy())
    total = len(tasks)
    completed = len([t for t in tasks if t.startswith("✅")])
    percentage = int((completed / total) * 100) if total > 0 else 0
    return f"📊 نسبة الإنجاز: {completed}/{total} ({percentage}%)"

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.from_user.id
    if user_id not in user_tasks:
        user_tasks[user_id] = default_tasks.copy()
    progress = get_task_progress_text(user_id)
    bot.send_message(user_id, f"{progress}\n\nاضغط على المهام لإنجازها ✅", reply_markup=generate_task_keyboard(user_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def task_done_handler(call):
    user_id = call.from_user.id
    index = int(call.data.split("_")[1])
    tasks = user_tasks.get(user_id, default_tasks.copy())

    if not tasks[index].startswith("✅"):
        task_name = tasks[index]
        tasks[index] = "✅ " + task_name
        user_tasks[user_id] = tasks
        progress = get_task_progress_text(user_id)

        # تحديث الرسالة الأصلية
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{progress}\n\nاضغط على المهام لإنجازها ✅",
            reply_markup=generate_task_keyboard(user_id)
        )

        # إرسال رسالة تشجيعية
        bot.send_message(user_id, f"أحسنت! لقد أنجزت المهمة ✅: {task_name}")

@bot.message_handler(func=lambda msg: msg.text)
def add_task_handler(message):
    user_id = message.from_user.id
    new_task = message.text.strip()
    if user_id not in user_tasks:
        user_tasks[user_id] = default_tasks.copy()
    user_tasks[user_id].append(new_task)
    bot.reply_to(message, f"تمت إضافة المهمة: {new_task}")

# ✅ وظيفة إعادة المهام يومياً الساعة 3 فجراً
def daily_reset():
    while True:
        now = datetime.now()
        if now.hour == 3 and now.minute == 0:
            for user_id in user_tasks:
                user_tasks[user_id] = default_tasks.copy()
                bot.send_message(user_id, "☀️ مهام يوم جديد:\n" + get_task_progress_text(user_id), reply_markup=generate_task_keyboard(user_id))
            time.sleep(60)  # انتظر دقيقة عشان ما يعيد الإرسال
        time.sleep(30)

# تشغيل المهام الخلفية
reset_thread = threading.Thread(target=daily_reset)
reset_thread.daemon = True
reset_thread.start()

bot.infinity_polling()
