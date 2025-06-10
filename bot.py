import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import threading
import time

TOKEN = "7660821828:AAG4j8ECarjnhVQMZBeT3WzLrZQ3ZmBXqSQ"
bot = telebot.TeleBot(TOKEN)

default_tasks = [
    "صلاة الفجر",
    "اذكار بعد صلاة الفجر",
    "الدعاء بعد صلاة الفجر",
    "اذكار الصباح",
    "صلاة الضحى",
    "الدعاء بعد صلاة الضحى",
    "الرقية الشرعية",
    "صلاة الظهر فرض وسنة",
    "اذكار بعد صلاة الظهر",
    "الدعاء بعد صلاة الظهر",
    "نصف جزء من القرآن الفترة النهارية",
    "استغفار وتسبيح وتهليل وتكبير بشكل كبير",
    "صلاة العصر",
    "اذكار بعد صلاة العرصر",
    "الدعاء بعد صلاة العصر",
    "اذكار المساء",
    "صلاة المغرب والسنة",
    "اذكار بعد صلاة المغرب",
    "الدعاء بعد صلاة المغرب",
    "صلاة العشاء والسنة",
    "اذكار بعد صلاة العشاء",
    "الدعاء بعد صلاة العشاء",
    "صلاة القيام على الأقل 4+ ركعات",
    "نصف جزء من القرآن الفترة الليلية",
    "أستغفار/تسبيح/تهليل/تكبير بشكل كبير",
    "الدعاء",
    "الشفع والوتر"
]

user_tasks = {}

def get_task_progress_text(user_id):
    tasks = user_tasks.get(user_id, default_tasks.copy())
    total = len(tasks)
    completed = len([t for t in tasks if t.startswith("✅")])
    percentage = int((completed / total) * 100) if total > 0 else 0
    return f"📊 نسبة الإنجاز: {completed}/{total} ({percentage}%)"

def generate_task_keyboard(user_id):
    tasks = user_tasks.get(user_id, default_tasks.copy())
    keyboard = InlineKeyboardMarkup(row_width=1)
    for i, task in enumerate(tasks):
        display = task
        if task.startswith("✅"):
            display = task
        else:
            display = f"🔲 {task}"
        keyboard.add(InlineKeyboardButton(display, callback_data=f"done_{i}"))
    return keyboard

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.from_user.id
    if user_id not in user_tasks:
        user_tasks[user_id] = default_tasks.copy()

    progress = get_task_progress_text(user_id)
    bot.send_message(
        message.chat.id,
        f"{progress}\n\n📝 مهامك لليوم:\n\nاضغط على المهام لإنجازها ✅",
        reply_markup=generate_task_keyboard(user_id)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def task_done_handler(call):
    user_id = call.from_user.id
    index = int(call.data.split("_")[1])
    tasks = user_tasks.get(user_id, default_tasks.copy())

    if not tasks[index].startswith("✅"):
        task_name = tasks[index]
        tasks[index] = "✅ " + tasks[index]
        user_tasks[user_id] = tasks

        progress = get_task_progress_text(user_id)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"{progress}\n\n📝 مهامك لليوم:\n\nاضغط على المهام لإنجازها ✅",
            reply_markup=generate_task_keyboard(user_id)
        )

        bot.send_message(user_id, f"أحسنت! لقد أنجزت المهمة ✅: {task_name}")

# إعادة تعيين المهام يوميًا الساعة 3 فجراً
def reset_tasks_daily():
    while True:
        now = datetime.now()
        target = now.replace(hour=3, minute=0, second=0, microsecond=0)
        if now > target:
            target += timedelta(days=1)
        sleep_time = (target - now).total_seconds()
        time.sleep(sleep_time)

        for user_id in user_tasks:
            user_tasks[user_id] = default_tasks.copy()
            bot.send_message(user_id, "🕒 يوم جديد! هذه مهامك لليوم 👇", reply_markup=generate_task_keyboard(user_id))

# تشغيل مؤقت المهام اليومية
threading.Thread(target=reset_tasks_daily, daemon=True).start()

bot.infinity_polling()
