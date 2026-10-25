# import os
# import logging
# import telebot
# from dotenv import load_dotenv
# from telebot.types import ReplyKeyboardMarkup, KeyboardButton


# # --------------------------------------------------
# # Configuration
# # --------------------------------------------------

# load_dotenv()

# BOT_TOKEN = os.getenv("BOT_TOKEN")
# ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", "0"))
# SUGGESTIONS_TOPIC_ID = int(os.getenv("SUGGESTIONS_TOPIC_ID", "0"))
# EVENTS_TOPIC_ID = int(os.getenv("EVENTS_TOPIC_ID", "0"))

# if not BOT_TOKEN or not ADMIN_GROUP_ID:
#     raise ValueError(
#         "BOT_TOKEN و ADMIN_GROUP_ID باید در فایل .env تنظیم شوند."
#     )

# if not SUGGESTIONS_TOPIC_ID or not EVENTS_TOPIC_ID:
#     raise ValueError(
#         "SUGGESTIONS_TOPIC_ID و EVENTS_TOPIC_ID "
#         "باید در فایل .env تنظیم شوند."
#     )

# bot = telebot.TeleBot(BOT_TOKEN)

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# # --------------------------------------------------
# # Buttons
# # --------------------------------------------------

# SUGGESTIONS_BUTTON = "مطالبات و پیشنهادات"
# EVENTS_BUTTON = "ارسال اطلاعات رویدادها"
# CANCEL_BUTTON = "❌ انصراف"

# CAMPUSES = [
#     "پردیس مهریز",
#     "هنر و معماری",
#     "علوم انسانی",
#     "فنی مهندسی",
#     "منابع طبیعی",
#     "علوم پایه",
#     "بین رشته ای",
# ]


# def main_menu():
#     keyboard = ReplyKeyboardMarkup(
#         resize_keyboard=True
#     )
#     keyboard.row(SUGGESTIONS_BUTTON)
#     keyboard.row(EVENTS_BUTTON)
#     return keyboard


# def campus_menu():
#     keyboard = ReplyKeyboardMarkup(
#         resize_keyboard=True
#     )

#     keyboard.add(KeyboardButton("پردیس مهریز"),KeyboardButton("هنر و معماری"))
#     keyboard.add(KeyboardButton("علوم انسانی"),KeyboardButton("فنی مهندسی"))
#     keyboard.add(KeyboardButton("منابع طبیعی"),KeyboardButton("علوم پایه"))
#     keyboard.add(KeyboardButton("بین رشته‌ای"))
#     keyboard.add(KeyboardButton(CANCEL_BUTTON))
#     return keyboard


# def cancel_menu():
#     keyboard = ReplyKeyboardMarkup(
#         resize_keyboard=True
#     )
#     keyboard.add(KeyboardButton(CANCEL_BUTTON))
#     return keyboard


# # --------------------------------------------------
# # User states
# # --------------------------------------------------

# # حالت‌های مورد استفاده:
# # choosing_campus
# # waiting_suggestion
# # waiting_event_photo
# # waiting_event_caption

# user_states = {}
# user_campuses = {}
# event_poster_message_ids = {}


# # --------------------------------------------------
# # Admin group helpers
# # --------------------------------------------------

# def send_to_admin_group(text, topic_id):
#     """ارسال پیام متنی به تاپیک مشخص‌شده."""
#     return bot.send_message(
#         chat_id=ADMIN_GROUP_ID,
#         text=text,
#         message_thread_id=topic_id
#     )


# def sender_info(user):
#     """ساخت مشخصات ارسال‌کننده."""
#     full_name = " ".join(
#         part for part in [user.first_name, user.last_name]
#         if part
#     )

#     username = (
#         f"@{user.username}"
#         if user.username
#         else "ندارد"
#     )

#     return (
#         f"👤 نام: {full_name or 'ثبت نشده'}\n"
#         f"🔗 نام کاربری: {username}"
#     )


# def cancel_user_flow(user_id):
#     user_states.pop(user_id, None)
#     user_campuses.pop(user_id, None)
#     event_poster_message_ids.pop(user_id, None)


# # --------------------------------------------------
# # Commands
# # --------------------------------------------------

# @bot.message_handler(commands=["start"])
# def start(message):
#     cancel_user_flow(message.from_user.id)

#     bot.send_message(
#         message.chat.id,
#         """سلام👋🏻
#         ✨به ربات پشتیبان شورای اجرایی مجمع انجمن های علمی دانشگاه یزد خوش آمدید
#         لطفا از بین گزینه های زیر یکی را انتخاب کنید""",
#         reply_markup=main_menu()
#     )


# @bot.message_handler(commands=["cancel"])
# def cancel_command(message):
#     cancel_user_flow(message.from_user.id)

#     bot.send_message(
#         message.chat.id,
#         "عملیات لغو شد.",
#         reply_markup=main_menu()
#     )


# @bot.message_handler(commands=["chatid"])
# def get_chat_id(message):
#     bot.reply_to(
#         message,
#         f"Chat ID: {message.chat.id}"
#     )


# @bot.message_handler(commands=["topicid"])
# def get_topic_id(message):
#     thread_id = getattr(
#         message,
#         "message_thread_id",
#         None
#     )

#     bot.reply_to(
#         message,
#         f"Group ID: {message.chat.id}\n"
#         f"Topic ID: {thread_id}"
#     )


# # --------------------------------------------------
# # Main menu and text flows
# # --------------------------------------------------

# @bot.message_handler(
#     content_types=["text"],
#     func=lambda message: True
# )
# def handle_text(message):
#     user_id = message.from_user.id
#     text = message.text.strip()

#     # Cancel button
#     if text == CANCEL_BUTTON:
#         cancel_user_flow(user_id)

#         bot.send_message(
#             message.chat.id,
#             "عملیات لغو شد.",
#             reply_markup=main_menu()
#         )
#         return

#     # Main menu: suggestions
#     if text == SUGGESTIONS_BUTTON:
#         cancel_user_flow(user_id)
#         user_states[user_id] = "choosing_campus"

#         bot.send_message(
#             message.chat.id,
#             "لطفاً پردیس خودتون رو انتخاب کنید:",
#             reply_markup=campus_menu()
#         )
#         return

#     # Main menu: event information
#     if text == EVENTS_BUTTON:
#         cancel_user_flow(user_id)
#         user_states[user_id] = "waiting_event_photo"

#         bot.send_message(
#             message.chat.id,
#             "لطفاً پوستر رویداد رو به‌صورت عکس ارسال کنید:",
#             reply_markup=cancel_menu()
#         )
#         return

#     state = user_states.get(user_id)

#     # Campus selection
#     if state == "choosing_campus":
#         if text not in CAMPUSES:
#             bot.send_message(
#                 message.chat.id,
#                 "لطفاً یکی از پردیس‌های موجود در منو رو انتخاب کنید.",
#                 reply_markup=campus_menu()
#             )
#             return

#         user_campuses[user_id] = text
#         user_states[user_id] = "waiting_suggestion"

#         bot.send_message(
#             message.chat.id,
#             "لطفاً مطالبه یا پیشنهاد خود را بنویسید:",
#             reply_markup=cancel_menu()
#         )
#         return

#     # Receive suggestion
#     if state == "waiting_suggestion":
#         campus = user_campuses.get(
#             user_id,
#             "نامشخص"
#         )

#         admin_text = (
#             "📩 مطالبه یا پیشنهاد جدید\n\n"
#             f"🏢 پردیس: {campus}\n"
#             f"{sender_info(message.from_user)}\n\n"
#             f"📝 متن:\n{text}"
#         )

#         send_to_admin_group(
#             admin_text,
#             SUGGESTIONS_TOPIC_ID
#         )

#         cancel_user_flow(user_id)

#         bot.send_message(
#             message.chat.id,
#             "✅ مطالبه یا پیشنهاد شما با موفقیت ارسال شد.",
#             reply_markup=main_menu()
#         )
#         return

#     # Receive event caption
#     if state == "waiting_event_caption":
#         poster_message_id = event_poster_message_ids.get(
#             user_id
#         )

#         if not poster_message_id:
#             cancel_user_flow(user_id)

#             bot.send_message(
#                 message.chat.id,
#                 "شناسه پوستر پیدا نشد. لطفاً دوباره شروع کنید.",
#                 reply_markup=main_menu()
#             )
#             return

#         # Copy the original message to preserve formatting
#         # and embedded links.
#         bot.copy_message(
#             chat_id=ADMIN_GROUP_ID,
#             from_chat_id=message.chat.id,
#             message_id=message.message_id,
#             message_thread_id=EVENTS_TOPIC_ID,
#             reply_to_message_id=poster_message_id
#         )

#         # Send sender information as a separate reply
#         bot.send_message(
#             chat_id=ADMIN_GROUP_ID,
#             text=sender_info(message.from_user),
#             message_thread_id=EVENTS_TOPIC_ID,
#             reply_to_message_id=poster_message_id
#         )

#         cancel_user_flow(user_id)

#         bot.send_message(
#             message.chat.id,
#             "✅ اطلاعات رویداد با موفقیت ارسال شد.",
#             reply_markup=main_menu()
#         )
#         return

#     # Default response
#     bot.send_message(
#         message.chat.id,
#         "لطفاً یکی از گزینه‌های منو رو انتخاب کنید.",
#         reply_markup=main_menu()
#     )


# # --------------------------------------------------
# # Photo handler
# # --------------------------------------------------

# @bot.message_handler(content_types=["photo"])
# def handle_photo(message):
#     user_id = message.from_user.id
#     state = user_states.get(user_id)

#     if state != "waiting_event_photo":
#         return

#     # Send poster to the events topic
#     sent_poster = bot.send_photo(
#         chat_id=ADMIN_GROUP_ID,
#         photo=message.photo[-1].file_id,
#         caption="📌 پوستر رویداد جدید",
#         message_thread_id=EVENTS_TOPIC_ID
#     )

#     event_poster_message_ids[user_id] = (
#         sent_poster.message_id
#     )

#     # Send sender information as a reply to the poster
#     bot.send_message(
#         chat_id=ADMIN_GROUP_ID,
#         text=sender_info(message.from_user),
#         message_thread_id=EVENTS_TOPIC_ID,
#         reply_to_message_id=sent_poster.message_id
#     )

#     user_states[user_id] = "waiting_event_caption"

#     bot.send_message(
#         message.chat.id,
#         "لطفاً توضیحات رویداد رو در پیام بعدی ارسال کنید. "
#         "می‌تونید متن، لینک و قالب‌بندی دلخواهتون رو داشته باشید.",
#         reply_markup=cancel_menu()
#     )


# # --------------------------------------------------
# # Other media while waiting for text/photo
# # --------------------------------------------------

# @bot.message_handler(
#     content_types=[
#         "document",
#         "video",
#         "audio",
#         "voice",
#         "sticker",
#         "animation",
#         "video_note",
#         "location",
#         "contact"
#     ]
# )
# def handle_other_media(message):
#     user_id = message.from_user.id
#     state = user_states.get(user_id)

#     if state == "waiting_event_photo":
#         bot.send_message(
#             message.chat.id,
#             "لطفاً پوستر رو به‌صورت عکس ارسال کنید.",
#             reply_markup=cancel_menu()
#         )

#     elif state == "waiting_event_caption":
#         bot.send_message(
#             message.chat.id,
#             "لطفاً توضیحات رویداد رو به‌صورت پیام متنی ارسال کنید.",
#             reply_markup=cancel_menu()
#         )

#     elif state == "waiting_suggestion":
#         bot.send_message(
#             message.chat.id,
#             "لطفاً مطالبه یا پیشنهاد خود را به‌صورت متن ارسال کنید.",
#             reply_markup=cancel_menu()
#         )


# # --------------------------------------------------
# # Run bot
# # --------------------------------------------------

# if __name__ == "__main__":
#     logger.info("Bot started.")
#     bot.infinity_polling(
#         skip_pending=True,
#         allowed_updates=["message"]
#     )



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
event_poster_message_ids = {}


def clear_user_data(user_id):
    user_states.pop(user_id, None)
    user_campuses.pop(user_id, None)
    event_poster_message_ids.pop(user_id, None)


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
    keyboard.row(
        types.KeyboardButton(BTN_EVENTS)
    )

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

    # ----------------------------------------------
    # شروع ارسال اطلاعات رویداد
    # ----------------------------------------------

    # if text == BTN_EVENTS:
    #     clear_user_data(user_id)

    #     user_states[user_id] = "event_choose_campus"

    #     bot.send_message(
    #         message.chat.id,
    #         "📌 برای ارسال اطلاعات رویداد، "
    #         "ابتدا پردیس برگزارکننده رو انتخاب کنید:",
    #         reply_markup=campus_menu()
    #     )
    #     return

    # ----------------------------------------------
    # انتخاب پردیس برای مطالبه یا پیشنهاد
    # ----------------------------------------------

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

    # ----------------------------------------------
    # انتخاب پردیس برای ارسال رویداد
    # ----------------------------------------------

    # if state == "event_choose_campus":
    #     if text not in CAMPUSES:
    #         bot.send_message(
    #             message.chat.id,
    #             "لطفاً یکی از پردیس‌های موجود در منو رو انتخاب کنید.",
    #             reply_markup=campus_menu()
    #         )
    #         return

    #     user_campuses[user_id] = text
    #     user_states[user_id] = "waiting_event_photo"

    #     bot.send_message(
    #         message.chat.id,
    #         f"🏢 پردیس انتخاب‌شده: {text}\n\n"
    #         "🖼️ حالا لطفاً پوستر رویداد رو به‌صورت عکس ارسال کنید:",
    #         reply_markup=cancel_menu()
    #     )
    #     return

    # ----------------------------------------------
    # دریافت توضیحات رویداد
    # ----------------------------------------------

    # if state == "waiting_event_caption":
    #     poster_message_id = event_poster_message_ids.get(
    #         user_id
    #     )

    #     if not poster_message_id:
    #         clear_user_data(user_id)

    #         bot.send_message(
    #             message.chat.id,
    #             "متأسفانه اطلاعات پوستر پیدا نشد. "
    #             "لطفاً دوباره از منوی اصلی شروع کنید.",
    #             reply_markup=main_menu()
    #         )
    #         return

    #     campus = user_campuses.get(
    #         user_id,
    #         "نامشخص"
    #     )

        # ارسال توضیحات با حفظ قالب‌بندی و لینک‌ها
        # bot.copy_message(
        #     chat_id=ADMIN_GROUP_ID,
        #     from_chat_id=message.chat.id,
        #     message_id=message.message_id,
        #     message_thread_id=EVENTS_TOPIC_ID,
        #     reply_to_message_id=poster_message_id
        # )

        # # ارسال مشخصات فرستنده و پردیس در پاسخ به پوستر
        # bot.send_message(
        #     chat_id=ADMIN_GROUP_ID,
        #     text=(
        #         f"🏢 پردیس برگزارکننده: {campus}\n"
        #         f"{sender_info(message.from_user)}"
        #     ),
        #     message_thread_id=EVENTS_TOPIC_ID,
        #     reply_to_message_id=poster_message_id
        # )

        # clear_user_data(user_id)

        # bot.send_message(
        #     message.chat.id,
        #     "✅ اطلاعات رویداد شما با موفقیت ارسال شد.",
        #     reply_markup=main_menu()
        # )
        # return

    # ----------------------------------------------
    # پیام پیش‌فرض
    # ----------------------------------------------

    bot.send_message(
        message.chat.id,
        "لطفاً یکی از گزینه‌های منو رو انتخاب کنید.",
        reply_markup=main_menu()
    )


# ==================================================
# دریافت پوستر رویداد
# ==================================================

# @bot.message_handler(content_types=["photo"])
# def handle_photo(message):
#     user_id = message.from_user.id
#     state = user_states.get(user_id)

#     if state != "waiting_event_photo":
#         return

#     campus = user_campuses.get(
#         user_id,
#         "نامشخص"
#     )

#     # ارسال پوستر به تاپیک رویدادها
#     sent_poster = bot.send_photo(
#         chat_id=ADMIN_GROUP_ID,
#         photo=message.photo[-1].file_id,
#         caption=(
#             "📌 پوستر رویداد جدید\n"
#             f"🏢 پردیس: {campus}"
#         ),
#         message_thread_id=EVENTS_TOPIC_ID
#     )

#     event_poster_message_ids[user_id] = (
#         sent_poster.message_id
#     )

#     # مشخصات فرستنده در پاسخ به پوستر
#     bot.send_message(
#         chat_id=ADMIN_GROUP_ID,
#         text=sender_info(message.from_user),
#         message_thread_id=EVENTS_TOPIC_ID,
#         reply_to_message_id=sent_poster.message_id
#     )

#     user_states[user_id] = "waiting_event_caption"

#     bot.send_message(
#         message.chat.id,
#         "📝 حالا توضیحات رویداد رو در پیام بعدی ارسال کنید.\n\n"
#         "می‌تونید متن، لینک و قالب‌بندی دلخواهتون رو "
#         "در همون پیام قرار بدید.",
#         reply_markup=cancel_menu()
#     )


# ==================================================
# مدیریت رسانه‌های نامعتبر در مراحل دریافت اطلاعات
# ==================================================

# @bot.message_handler(
#     content_types=[
#         "document",
#         "video",
#         "audio",
#         "voice",
#         "sticker",
#         "animation",
#         "video_note",
#         "location",
#         "contact"
#     ]
# )
# def handle_other_media(message):
#     user_id = message.from_user.id
#     state = user_states.get(user_id)

#     if state == "waiting_event_photo":
#         bot.send_message(
#             message.chat.id,
#             "لطفاً پوستر رو به‌صورت عکس ارسال کنید.",
#             reply_markup=cancel_menu()
#         )

#     elif state == "waiting_event_caption":
#         bot.send_message(
#             message.chat.id,
#             "لطفاً توضیحات رویداد رو به‌صورت پیام متنی ارسال کنید.",
#             reply_markup=cancel_menu()
#         )

#     elif state == "waiting_suggestion":
#         bot.send_message(
#             message.chat.id,
#             "لطفاً مطالبه یا پیشنهاد خودتون رو به‌صورت متن ارسال کنید.",
#             reply_markup=cancel_menu()
#         )


# ==================================================
# اجرای ربات
# ==================================================

if __name__ == "__main__":
    logger.info("Bot started.")

    bot.infinity_polling(
        skip_pending=True,
        allowed_updates=["message"]
    )
