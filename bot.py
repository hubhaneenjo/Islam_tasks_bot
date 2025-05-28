import telebot

# حطي التوكن تبعك من BotFather هون
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

def get_task_list(user_id):
    tasks = user_tasks.get(user_id, default_tasks.copy())

    total = len(tasks)
    completed = len([t for t in tasks if t.startswith("✅")])
    percentage = int((completed / total) * 100) if total > 0 else 0

    formatted = "\n".join([f"{'✅' if t.startswith('✅') else '🔲'} {t.lstrip('✅ ').strip()}" for t in tasks])
    return f"📊 نسبة الإنجاز: {completed}/{total} ({percentage}%)\n\n📝 مهامك اليوم:\n\n{formatted}"

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in user_tasks:
        user_tasks[user_id] = default_tasks.copy()
    bot.reply_to(message, get_task_list(user_id) + "\n\nاكتب مهمة جديدة لإضافتها ✅")

@bot.message_handler(func=lambda msg: msg.text)
def add_or_check_task(message):
    user_id = message.from_user.id
    task_text = message.text.strip()

    tasks = user_tasks.get(user_id, default_tasks.copy())

    # إذا كانت المهمة موجودة، نشطبها
    for i, task in enumerate(tasks):
        if task_text in task and not task.startswith("✅"):
            tasks[i] = f"✅ {task}"
            user_tasks[user_id] = tasks
            bot.reply_to(message, f"أحسنت! ✅ أنجزت: {task_text}")
            return

    # إذا مش موجودة، نضيفها
    tasks.append(task_text)
    user_tasks[user_id] = tasks
    bot.reply_to(message, f"تمت إضافة المهمة: {task_text}")

bot.infinity_polling()
