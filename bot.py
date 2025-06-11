import telebot
from telebot import types
import os
import threading
import time
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")  # أو ضعي التوكن مباشرة بين "" لو مو مستعملة متغير بيئة
bot = telebot.TeleBot(TOKEN)

# المهام الافتراضية
default_tasks = [
    "☀️ صلاة الفجر 🧎‍♂️", "اذكار بعد صلاة الفجر 📕", "الدعاء بعد صلاة الفجر 🤲", "اذكار الصباح ",
    "🧎‍♂️ صلاة الضحى 🧎‍♂️", "الدعاء بعد صلاة الضحى 🤲", "الرقية الشرعية 🙏", "صلاة الظهر فرض وسنة",
    "📖 اذكار بعد صلاة الظهر 📕", "الدعاء بعد صلاة الظهر 🤲", "نصف جزء من القرآن",
    "📕 استغفار وتسبيح وتهليل وتكبير بشكل كبير 📿", "صلاة العصر 🧎‍♂️", "اذكار بعد صلاة العصر",
    "📕 الدعاء بعد صلاة العصر 🤲", "اذكار المساء 🌙", "صلاة المغرب والسنة 🧎‍♂️", "اذكار بعد صلاة المغرب",
    "📕 الدعاء بعد صلاة المغرب 🤲 ", "صلاة العشاء والسنة والشفع والوتر 🧎‍♂️", "اذكار بعد صلاة العشاء",
    "🥺 الدعاء بعد صلاة العشاء 🤲", "صلاة القيام على الأقل 2+ ركعات",
    "🤲 أستغفار/تسبيح/تهليل/تكبير بشكل كبير 📿","الدعاء"
]

user_tasks = {}
user_states = {}

def generate_task_keyboard(user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    tasks = user_tasks.get(user_id, default_tasks.copy())
    buttons = []
    for i, task in enumerate(tasks):
        if task.startswith("✅"):
            continue
        button = types.InlineKeyboardButton(text=task, callback_data=f"done_{i}")
        buttons.append(button)
    add_task_btn = types.InlineKeyboardButton("➕ إضافة مهمة", callback_data="add_task")
    markup.add(*buttons)
    markup.add(add_task_btn)
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

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{progress}\n\nاضغط على المهام لإنجازها ✅",
            reply_markup=generate_task_keyboard(user_id)
        )
        bot.send_message(user_id, f"أحسنت! لقد أنجزت المهمة ✅: {task_name}")

@bot.callback_query_handler(func=lambda call: call.data == "add_task")
def add_task_callback(call):
    user_id = call.from_user.id
    user_states[user_id] = "awaiting_new_task"
    bot.send_message(user_id, "📌 أرسل المهمة الجديدة التي تريد إضافتها:")

@bot.message_handler(func=lambda msg: True)
def handle_messages(message):
    user_id = message.from_user.id
    if user_states.get(user_id) == "awaiting_new_task":
        new_task = message.text.strip()
        if user_id not in user_tasks:
            user_tasks[user_id] = default_tasks.copy()
        user_tasks[user_id].append(new_task)
        user_states.pop(user_id, None)
        bot.reply_to(message, f"✅ تمت إضافة المهمة: {new_task}")
    else:
        bot.send_message(user_id, "✉️ استخدم الأزرار لإدارة المهام أو /start للبدء")

# ✅ وظيفة إعادة المهام يومياً الساعة 3 فجراً + إرسال رسالة التقييم 2:30 فجراً
def daily_routines():
    while True:
        now = datetime.now()
        if now.hour == 2 and now.minute == 30:
            for user_id in user_tasks:
                tasks = user_tasks.get(user_id, default_tasks.copy())
                completed = all(t.startswith("✅") for t in tasks)
                if completed:
                    bot.send_message(user_id, "💯 ممتاز ، تقبل الله طاعاتك انجزت كافة المهام")
                else:
                    bot.send_message(user_id, "🌟 جزاك الله خيراً ، ستكون أفضل في المرة القادمة")
            time.sleep(60)

        if now.hour == 3 and now.minute == 0:
            for user_id in user_tasks:
                user_tasks[user_id] = default_tasks.copy()
                bot.send_message(user_id, "☀️ مهام يوم جديد:\n" + get_task_progress_text(user_id), reply_markup=generate_task_keyboard(user_id))
            time.sleep(60)

        time.sleep(30)

# تشغيل المهام الخلفية
routine_thread = threading.Thread(target=daily_routines)
routine_thread.daemon = True
routine_thread.start()

bot.infinity_polling()
