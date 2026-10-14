import os
import logging
import telebot
from telebot import types
from dotenv import load_dotenv


# -------------------- Configuration --------------------

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN در فایل .env تنظیم نشده است.")

bot = telebot.TeleBot(BOT_TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -------------------- Menus --------------------

BTN_SUGGESTIONS = "مطالبات و پیشنهادات"
BTN_EVENTS = "ارسال اطلاعات رویدادها"
BTN_CANCEL = "❌ انصراف"

# وضعیت موقت هر کاربر؛ بدون دیتابیس
user_states = {}

# شناسه پیام پوستر در گروه ادمین‌ها
event_poster_message_ids = {}


def main_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=1
    )

    keyboard.add(
        types.KeyboardButton(BTN_SUGGESTIONS),
        types.KeyboardButton(BTN_EVENTS)
    )

    return keyboard


def cancel_menu():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    keyboard.add(types.KeyboardButton(BTN_CANCEL))
    return keyboard


# -------------------- Helpers --------------------

def get_sender_info(message):
    user = message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )

    # شناسه تلگرام کاربر در پیام گروه نمایش داده نمی‌شود
    return (
        f"نام: {user.first_name or 'ندارد'}\n"
        f"نام کاربری: {username}"
    )


def send_to_admin_group(text):
    if not ADMIN_GROUP_ID:
        logger.warning(
            "ADMIN_GROUP_ID تنظیم نشده است. پیام ارسال نشد."
        )
        return False

    try:
        bot.send_message(
            int(ADMIN_GROUP_ID),
            text
        )
        return True

    except Exception:
        logger.exception("خطا در ارسال پیام به گروه ادمین‌ها")
        return False


# -------------------- Start --------------------

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    user_states.pop(user_id, None)
    event_poster_message_ids.pop(user_id, None)

    bot.send_message(
        message.chat.id,
        "سلام، به ربات پشتیبان شورای اجرایی خوش آمدید.\n"
        "لطفاً از بین گزینه‌های زیر یکی را انتخاب کنید.",
        reply_markup=main_menu()
    )


@bot.message_handler(commands=["cancel"])
def cancel_command(message):
    user_id = message.from_user.id

    user_states.pop(user_id, None)
    event_poster_message_ids.pop(user_id, None)

    bot.send_message(
        message.chat.id,
        "عملیات لغو شد. به منوی اصلی برگشتید.",
        reply_markup=main_menu()
    )


# -------------------- Find Admin Group ID --------------------

@bot.message_handler(commands=["chatid"])
def get_chat_id(message):
    bot.reply_to(
        message,
        f"شناسه این گفتگو:\n{message.chat.id}"
    )

    logger.info(
        "Chat ID: %s | Chat type: %s",
        message.chat.id,
        message.chat.type
    )


# -------------------- Suggestions --------------------

@bot.message_handler(
    func=lambda message: message.text == BTN_SUGGESTIONS
)
def suggestions_start(message):
    user_states[message.from_user.id] = "suggestion"

    bot.send_message(
        message.chat.id,
        "لطفاً مطالبه یا پیشنهاد خود را ارسال کنید:",
        reply_markup=cancel_menu()
    )


# -------------------- Event Information --------------------

@bot.message_handler(
    func=lambda message: message.text == BTN_EVENTS
)
def event_start(message):
    user_id = message.from_user.id

    user_states[user_id] = "event_photo"
    event_poster_message_ids.pop(user_id, None)

    bot.send_message(
        message.chat.id,
        "لطفاً عکس پوستر رویداد خود را برای ما ارسال کنید.",
        reply_markup=cancel_menu()
    )


# -------------------- Cancel Button --------------------

@bot.message_handler(
    func=lambda message: message.text == BTN_CANCEL
)
def cancel_button(message):
    user_id = message.from_user.id

    user_states.pop(user_id, None)
    event_poster_message_ids.pop(user_id, None)

    bot.send_message(
        message.chat.id,
        "عملیات لغو شد. به منوی اصلی برگشتید.",
        reply_markup=main_menu()
    )


# -------------------- Receive Event Poster --------------------

@bot.message_handler(
    content_types=["photo"],
    func=lambda message: (
        user_states.get(message.from_user.id) == "event_photo"
    )
)
def receive_event_photo(message):
    user_id = message.from_user.id
    info = get_sender_info(message)

    if not ADMIN_GROUP_ID:
        bot.send_message(
            message.chat.id,
            "شناسه گروه ادمین‌ها هنوز تنظیم نشده است.",
            reply_markup=main_menu()
        )
        user_states.pop(user_id, None)
        return

    try:
        # ارسال پوستر به گروه ادمین‌ها
        sent_poster = bot.send_photo(
            int(ADMIN_GROUP_ID),
            message.photo[-1].file_id,
            caption=f"📌 پوستر رویداد جدید\n\n{info}"
        )

        # نگهداری شناسه پیام پوستر برای اتصال کپشن
        event_poster_message_ids[user_id] = (
            sent_poster.message_id
        )

        user_states[user_id] = "event_caption"

        bot.send_message(
            message.chat.id,
            "پوستر دریافت شد.\n"
            "حالا لطفاً متن کپشن پوستر رویداد را ارسال کنید.",
            reply_markup=cancel_menu()
        )

    except Exception:
        logger.exception("خطا در دریافت یا ارسال پوستر")

        user_states.pop(user_id, None)
        event_poster_message_ids.pop(user_id, None)

        bot.send_message(
            message.chat.id,
            "ارسال پوستر با خطا مواجه شد. لطفاً بعداً دوباره تلاش کنید.",
            reply_markup=main_menu()
        )


# -------------------- Receive Text --------------------

@bot.message_handler(content_types=["text"])
def receive_text(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if state == "suggestion":
        info = get_sender_info(message)

        success = send_to_admin_group(
            "📩 مطالبه یا پیشنهاد جدید\n\n"
            f"{info}\n\n"
            f"متن پیام:\n{message.text}"
        )

        user_states.pop(user_id, None)

        if success:
            bot.send_message(
                message.chat.id,
                "پیام شما با موفقیت ارسال شد. ممنون از همراهی شما 🌱",
                reply_markup=main_menu()
            )
        else:
            bot.send_message(
                message.chat.id,
                "ارسال پیام با مشکل مواجه شد. لطفاً بعداً تلاش کنید.",
                reply_markup=main_menu()
            )

        return

    if state == "event_caption":
        info = get_sender_info(message)
        poster_message_id = event_poster_message_ids.get(user_id)

        if not ADMIN_GROUP_ID or not poster_message_id:
            user_states.pop(user_id, None)
            event_poster_message_ids.pop(user_id, None)

            bot.send_message(
                message.chat.id,
                "اطلاعات پوستر پیدا نشد یا تنظیمات گروه ناقص است. "
                "لطفاً فرایند ارسال رویداد را دوباره آغاز کنید.",
                reply_markup=main_menu()
            )
            return

        try:
            # ارسال مشخصات فرستنده به‌عنوان پیام توضیحی
            bot.send_message(
                int(ADMIN_GROUP_ID),
                f"📝 کپشن رویداد جدید\n\n{info}",
                reply_to_message_id=poster_message_id
            )

            # کپی پیام اصلی برای حفظ لینک‌ها و قالب‌بندی
            # کپشن به پیام پوستر در گروه پاسخ داده می‌شود
            bot.copy_message(
                chat_id=int(ADMIN_GROUP_ID),
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                reply_to_message_id=poster_message_id
            )

            user_states.pop(user_id, None)
            event_poster_message_ids.pop(user_id, None)

            bot.send_message(
                message.chat.id,
                "اطلاعات رویداد شما دریافت شد. ممنون 🌱",
                reply_markup=main_menu()
            )

        except Exception:
            logger.exception("خطا در ارسال کپشن رویداد")

            bot.send_message(
                message.chat.id,
                "ارسال کپشن با مشکل مواجه شد. "
                "لطفاً دوباره تلاش کنید.",
                reply_markup=cancel_menu()
            )

        return

    if state == "event_photo":
        bot.send_message(
            message.chat.id,
            "لطفاً پوستر رویداد را به صورت عکس ارسال کنید.",
            reply_markup=cancel_menu()
        )
        return

    # انتخاب گزینه‌های منوی اصلی
    if message.text not in (BTN_SUGGESTIONS, BTN_EVENTS, BTN_CANCEL):
        bot.send_message(
            message.chat.id,
            "لطفاً یکی از گزینه‌های منوی اصلی را انتخاب کنید.",
            reply_markup=main_menu()
        )


# -------------------- Other Media --------------------

@bot.message_handler(
    content_types=["document", "video", "audio"]
)
def unsupported_media(message):
    state = user_states.get(message.from_user.id)

    if state == "event_photo":
        bot.send_message(
            message.chat.id,
            "لطفاً پوستر را به صورت عکس ارسال کنید."
        )

    elif state == "suggestion":
        bot.send_message(
            message.chat.id,
            "لطفاً مطالبه یا پیشنهاد خود را به صورت متن ارسال کنید."
        )

    elif state == "event_caption":
        bot.send_message(
            message.chat.id,
            "لطفاً کپشن پوستر را به صورت متن ارسال کنید."
        )


# -------------------- Run Bot --------------------

if __name__ == "__main__":
    logger.info("ربات پشتیبان شورای اجرایی فعال شد.")
    bot.infinity_polling(skip_pending=True)
