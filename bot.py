import os
import logging
import telebot
from telebot import types
from dotenv import load_dotenv
# ==================================================
# تنظیمات اولیه
# ==================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", "0"))
SUGGESTIONS_TOPIC_ID = int(os.getenv("SUGGESTIONS_TOPIC_ID", "0"))
EVENTS_TOPIC_ID = int(os.getenv("EVENTS_TOPIC_ID", "0"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN در فایل .env تنظیم نشده است.")

if not ADMIN_GROUP_ID:
    raise ValueError("ADMIN_GROUP_ID در فایل .env تنظیم نشده است.")

if not SUGGESTIONS_TOPIC_ID or not EVENTS_TOPIC_ID:
    raise ValueError("شناسه تاپیک‌ها در فایل .env تنظیم نشده است.")

bot = telebot.TeleBot(BOT_TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================================================
# متن‌ها و ثابت‌ها
# ==================================================

BTN_SUGGESTIONS = "مطالبات و پیشنهادات"
# BTN_EVENTS = "ارسال اطلاعات رویدادها"
BTN_CANCEL = "❌ انصراف"
BTN_BACK = "🔙 بازگشت به منوی اصلی"

CAMPUSES = [
    "پردیس مهریز",
    "هنر و معماری",
    "علوم انسانی",
    "فنی مهندسی",
    "منابع طبیعی",
    "علوم پایه",
    "بین رشته‌ای",
]


# ==================================================
# وضعیت کاربران
# ==================================================

user_states = {}
user_campuses = {}
# event_poster_message_ids = {}


def clear_user_data(user_id):
    user_states.pop(user_id, None)
    user_campuses.pop(user_id, None)
    # event_poster_message_ids.pop(user_id, None)


# ==================================================
# کیبوردها
# ==================================================

def main_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        types.KeyboardButton(BTN_SUGGESTIONS)
    )
    # keyboard.row(
    #     types.KeyboardButton(BTN_EVENTS)
    # )

    return keyboard


def campus_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.add(
        types.KeyboardButton("پردیس مهریز"),
        types.KeyboardButton("هنر و معماری")
    )
    keyboard.add(
        types.KeyboardButton("علوم انسانی"),
        types.KeyboardButton("فنی مهندسی")
    )
    keyboard.add(
        types.KeyboardButton("منابع طبیعی"),
        types.KeyboardButton("علوم پایه")
    )
    keyboard.add(
        types.KeyboardButton("بین رشته‌ای")
    )
    keyboard.add(
        types.KeyboardButton(BTN_CANCEL)
    )

    return keyboard


def cancel_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    keyboard.add(
        types.KeyboardButton(BTN_CANCEL)
    )

    return keyboard


# ==================================================
# ارسال به گروه و تاپیک مشخص
# ==================================================

def send_to_admin_group(text, topic_id):
    return bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=text,
        message_thread_id=topic_id
    )


def sender_info(user):
    full_name = " ".join(
        part
        for part in [user.first_name, user.last_name]
        if part
    )

    username = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )

    return (
        f"👤 نام: {full_name or 'ثبت نشده'}\n"
        f"🔗 نام کاربری: {username}\n"
        f"🆔 شناسه تلگرام: {user.id}"
    )


# ==================================================
# شروع ربات
# ==================================================

@bot.message_handler(commands=["start"])
def start(message):
    clear_user_data(message.from_user.id)

    welcome_text = (
        "سلام 👋🏻\n\n"
        "✨ به ربات پشتیبان شورای اجرایی "
        "مجمع انجمن‌های علمی دانشگاه یزد خوش آمدید.\n\n"
        "لطفاً از بین گزینه‌های زیر، یکی را انتخاب کنید 👇🏻"
    )

    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=main_menu()
    )


# ==================================================
# لغو عملیات
# ==================================================

@bot.message_handler(commands=["cancel"])
def cancel_command(message):
    clear_user_data(message.from_user.id)

    bot.send_message(
        message.chat.id,
        "عملیات لغو شد. 👌🏻",
        reply_markup=main_menu()
    )


# ==================================================
# نمایش شناسه گروه و تاپیک
# ==================================================

@bot.message_handler(commands=["chatid"])
def get_chat_id(message):
    bot.reply_to(
        message,
        f"Group ID: {message.chat.id}"
    )


@bot.message_handler(commands=["topicid"])
def get_topic_id(message):
    thread_id = getattr(
        message,
        "message_thread_id",
        None
    )

    bot.reply_to(
        message,
        f"Group ID: {message.chat.id}\n"
        f"Topic ID: {thread_id}"
    )


# ==================================================
# پردازش پیام‌های متنی
# ==================================================

@bot.message_handler(
    content_types=["text"],
    func=lambda message: True
)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()
    state = user_states.get(user_id)

    # ----------------------------------------------
    # دکمه انصراف
    # ----------------------------------------------

    if text == BTN_CANCEL:
        clear_user_data(user_id)

        bot.send_message(
            message.chat.id,
            "عملیات لغو شد. 👌🏻",
            reply_markup=main_menu()
        )
        return

    # ----------------------------------------------
    # بازگشت به منوی اصلی
    # ----------------------------------------------

    if text == BTN_BACK:
        clear_user_data(user_id)

        bot.send_message(
            message.chat.id,
            "به منوی اصلی برگشتید.",
            reply_markup=main_menu()
        )
        return

    # ----------------------------------------------
    # شروع مطالبات و پیشنهادات
    # ----------------------------------------------

    if text == BTN_SUGGESTIONS:
        clear_user_data(user_id)

        user_states[user_id] = "suggestion_choose_campus"

        bot.send_message(
            message.chat.id,
            "🏢 لطفاً پردیس خودتون رو انتخاب کنید:",
            reply_markup=campus_menu()
        )
        return


    if state == "suggestion_choose_campus":
        if text not in CAMPUSES:
            bot.send_message(
                message.chat.id,
                "لطفاً یکی از پردیس‌های موجود در منو رو انتخاب کنید.",
                reply_markup=campus_menu()
            )
            return

        user_campuses[user_id] = text
        user_states[user_id] = "waiting_suggestion"

        bot.send_message(
            message.chat.id,
            "📝 لطفاً مطالبه یا پیشنهاد خودتون رو بنویسید:",
            reply_markup=cancel_menu()
        )
        return

    # ----------------------------------------------
    # دریافت مطالبه یا پیشنهاد
    # ----------------------------------------------

    if state == "waiting_suggestion":
        campus = user_campuses.get(
            user_id,
            "نامشخص"
        )

        admin_text = (
            "📩 مطالبه یا پیشنهاد جدید\n\n"
            f"🏢 پردیس: {campus}\n"
            f"{sender_info(message.from_user)}\n\n"
            f"📝 متن:\n{text}"
        )

        send_to_admin_group(
            admin_text,
            SUGGESTIONS_TOPIC_ID
        )

        clear_user_data(user_id)

        bot.send_message(
            message.chat.id,
            "✅ مطالبه یا پیشنهاد شما با موفقیت ارسال شد.",
            reply_markup=main_menu()
        )
        return

    bot.send_message(
        message.chat.id,
        "لطفاً یکی از گزینه‌های منو رو انتخاب کنید.",
        reply_markup=main_menu())


if __name__ == "__main__":
    logger.info("Bot started.")

    bot.infinity_polling(
        skip_pending=True,
        allowed_updates=["message"]
    )