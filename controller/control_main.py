import json
import logging
import os
from datetime import datetime, timedelta

# Module View sending
from jobsView.view_main import ViewMain
from pushdb.add_update import add_signup_to_db
from pushdb.get_db import GetDatabase
from telegram import (Bot, CallbackQuery, ForceReply, InlineKeyboardButton,
                      InlineKeyboardMarkup, InlineQuery, KeyboardButton,
                      ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      ReplyMarkup, Update)

from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler)
# Telegram package
from telegram.utils.helpers import mention_html
# Module View for text
from templates.not_format import TextChat
from timezonefinder import TimezoneFinder
# Emoji
# Module for inline_button second state
# Module for the return second state
from utills.constants_cham import (
    BACK_FINISH, CHAT_ID, DATA_CONTACT, DATA_LATITUDE, DATA_LONGITUDE, DB_SAVE,
    END, EXIT_FOOTBALL, FINISH, FIRST, INLINE_CONF, LOCATION_FINISH, REMOVAL,
    SIGNUP, SIGNUP_STATE, SIGNUP_TOFINSIH, STACK_CONTACT, STACK_LOCATION,
    TODAY, TZINFO, USER_ID, USER_SIGNUP, USER_SUCCESS_SIGNUP, emoji_all,
    LIST_TEAM_FAV)
# Permession
from utills.permission import restricted_chat
from utills.ucallendar import TimeUtils

# Database Sqlalchemy
from pushdb.models import Session, UserData

# This for emoji
e_command = emoji_all['command']
e_cancel = emoji_all['cancel']
e_location = emoji_all['location']
e_hand = emoji_all['hello']
e_ngece = emoji_all['ngece']
e_ball = emoji_all['ball']
e_phone = emoji_all['contact']
old_zone = emoji_all['timezone']
e_correct = emoji_all['correct']

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# View
job_view = ViewMain()

@restricted_chat
def main_menu(update: Update, context: CallbackContext):
    """Begin(entry_points) for /football command (Top State)
    View component: `main_menu_view` in jobView/view_main.py
    """
    # The button for a user hasn't signup yet
    button_schedule_today = InlineKeyboardButton("SHEDULE TODAY",
                                                 callback_data=str(TODAY))
    button_signup_begin = InlineKeyboardButton("SIGNUP",
                                               callback_data=str(SIGNUP))
    button_exit = InlineKeyboardButton('EXIT',
                                       callback_data=str(EXIT_FOOTBALL))
    buttons = [[button_schedule_today], [button_signup_begin], [button_exit]]
    markup_nonsignup = InlineKeyboardMarkup(buttons)
    
    # The button already signup
    array_button = [[button_schedule_today], [button_exit]]
    markup_signup = InlineKeyboardMarkup(array_button)
    
    job_view.main_menu_view(update=update,
                            context=context,
                            markup_nonsignup=markup_nonsignup,
                            markup_signup=markup_signup)

    return SIGNUP_STATE

def msg_shedule(update: Update, context: CallbackContext):
    """The main responsibility of this handler is for the button SCHEDULE TODAY.
    View component: `message_everyday` in jobView/view_main.py
    Retun : back to the `main_menu` if a user has sig up the, button is for has signup vice versa
    """
    user = update.effective_user
    chat_id = update.effective_chat.id

    # InlineKeyboardButton callback_data
    buton_signup = InlineKeyboardButton("SIGNUP", callback_data=str(SIGNUP))
    button_exit = InlineKeyboardButton('EXIT', callback_data=str(EXIT_FOOTBALL))
    buttons = [[buton_signup], [button_exit]]
    # Button for a user non-signup
    reply_markup = InlineKeyboardMarkup(buttons)
    
    # Button for user has signup
    button_has_signup = [[button_exit]]
    reply_markup_has_signup = InlineKeyboardMarkup(button_has_signup)
    today_datetime = update.effective_message.date # unix timestamp
    if context.user_data.get(USER_SUCCESS_SIGNUP):
        # Don't get data time zone from Persistance data 
        session = Session()
        query_date = session.query(UserData).filter_by(chat_id=chat_id).first()
        logger.info(f'User: {query_date.username} SCHEDULE TODAY signup')

        convert_date = TimeUtils(unix_epoch=today_datetime,
                                 latit=query_date.latitude,
                                 longi=query_date.longitude)
        db_date = convert_date.time_aware()
        json_load = json.loads(db_date)
        dt = json_load['date']
        timezone_user = json_load['tzinfo']
        job_view.message_everyday(update, context,
                                  reply_menu=reply_markup_has_signup,
                                  str_tdate=dt,
                                  timezone_user=timezone_user)
    else:
        # None Timezone, default Asia/Jakarta timezone
        convert_date = TimeUtils(unix_epoch=today_datetime)
        db_date = convert_date.time_aware()
        json_load = json.loads(db_date)
        dt = json_load['date']
        timezone_user = json_load['tzinfo']
        job_view.message_everyday(update, context,
                                  reply_menu=reply_markup,
                                  str_tdate=dt,
                                  timezone_user=timezone_user)
    logger.info(f"User: {user.first_name} SCHEDULE TODAY. Date: {dt}")
    return FIRST


def signup_module(update: Update, context: CallbackContext):
    """Begin(entry_points) Second State.
    The main responsibility of this handler is for the costume keyboard contact.
    """

    user = update.effective_user

    # If user has signup
    if context.user_data.get(USER_SUCCESS_SIGNUP):
        # logger msg
        textchat = TextChat()
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=textchat.text_has_signup)
        return END
    else:
        # This for user will signup
        if update.callback_query:
            # logger msg
            msg_info = "signup_module User NON Login: {}".format(user)

            msg_id = update.callback_query.message.message_id
            context.bot.delete_message(chat_id=update.effective_chat.id,
                                       message_id=msg_id)

        text = (
            f"Send your phone number using keyboard custome {e_phone}\n"
            "\nIf you send with other method <b>Eg. message text or command</b>"
            f" you will <b>CANCEL</b> {e_cancel} SIGNUP session..!!"
            f" Also you can {e_cancel} cancel using keyboard costume.\n")

        contact_keyboard = KeyboardButton(text=f"CONTACT {e_phone}",
                                          request_contact=True)
        back_keyboard = KeyboardButton(text=f'CANCEL {e_cancel}')

        custom_keyboard = [[contact_keyboard], [back_keyboard]]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text,
                                 reply_markup=reply_markup)
    msg_info = "signup_module User have Login: {}".format(user.full_name)
    logger.info(msg_info)
    return STACK_CONTACT

def contact_signup(update: Update, context: CallbackContext):
    """The main responsibility of this handler is for the costume keyboard location."""

    contact = update.message.contact
    context.user_data[DATA_CONTACT] = str(contact.phone_number)
    
    # Caused user could be not have a first and last name contact
    if 0 == len(contact.first_name):
        context.user_data['name_contact'] = str(contact.last_name)
    else:
        context.user_data['name_contact'] = str(contact.first_name)

    location_keyboard = KeyboardButton(text=f"LOCATION {e_location}",
                                       request_location=True)
    back_keyboard = KeyboardButton(text=f'CANCEL {e_cancel}')
    custom_keyboard = [[location_keyboard], [back_keyboard]]
    text = (
        "Send your location using custome keyboard"
        f" {e_location} {e_location} {e_location}\n"
        f"Send your location correctly {e_correct}\n"
        f"it's for setting your <b>TIMEZONE</b> {e_location}\n"
        "\nIf you send with other method <b>Eg. message text or command</b>\n"
        " you will <b>CANCEL</b> 🔚 SIGNUP session..!!")

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             reply_markup=reply_markup,
                             parse_mode=ParseMode.HTML)
    logger.info("CONTACT of %s: Number: %s", contact.first_name,
                contact.phone_number)

    return STACK_LOCATION

def confirmation(update: Update, context: CallbackContext):
    """The main responsibility of this handler is for the button "YES Confirmation.
    Constanta variable from `utills/constants.py 
    Data will insert to database.
    username: update.message.from_user.username str
    LOCATION: float
    DATA_CONTACT phone_number: string
    USER_ID: update.effective_user.id or telegram.user.id int
    CHAT_ID: effective._chat.id int
    """
    # This importan don't place carelessly
    # Must before addd_signup_to_db
    context.user_data[CHAT_ID] = int(update.effective_chat.id)
    context.user_data[USER_ID] = int(update.effective_user.id)
    # Location
    user_location = update.message.location
    context.user_data[DATA_LATITUDE] = float(user_location.latitude)
    context.user_data[DATA_LONGITUDE] = float(user_location.longitude)
    # Convert latitude and longitude to tzinfo
    latitude = context.user_data[DATA_LATITUDE]
    longitude = context.user_data[DATA_LONGITUDE]
    tf = TimezoneFinder()
    tzinfo = tf.timezone_at(lng=longitude, lat=latitude)
    context.user_data[TZINFO] = tzinfo
    context.user_data['username'] = update.message.from_user.username
    username = context.user_data['username']

    # send message
    chat_id = update.effective_chat.id
    text_one = " 👀  ✔️ ✔️  "
    context.bot.send_message(chat_id=chat_id,
                             text=text_one,
                             reply_markup=ReplyKeyboardRemove(selective=True),
                             parse_mode=ParseMode.HTML)
    button_confirm = InlineKeyboardButton("YES Confirmation",
                                          callback_data=str(INLINE_CONF))
    button_cancel = InlineKeyboardButton("CANCEL",
                                         callback_data=str(f'CANCEL {e_cancel}'))
    buttons = [[button_confirm], [button_cancel]]

    button_send = InlineKeyboardMarkup(buttons)
    phone = context.user_data[DATA_CONTACT]
    text_two = (
        "If your data <b>incorrect</b> you can cancel and signup again.\n"
        "\n<b>YOUR DATA:</b> 📕\n"
        f"{old_zone}\n"
        f"<b>TIMEZONE: {tzinfo}</b>\n"
        f"{e_phone}\n"
        f"<b>PHONE NUMBER: {phone}</b>")
    context.bot.send_message(chat_id=chat_id,
                             text=text_two,
                             reply_markup=button_send)
    logger.info("User {} in confirmation".format(username))
    logger.info("LOCATION: %f / %f", user_location.latitude,
                user_location.longitude)

    return LOCATION_FINISH


def insert_db(update: Update, context: CallbackContext):
    """The main responsibility of this handler is insert data to the database 
    and end second conversation.
    Constans variable:
        USER_SUCCESS_SIGNUP: Give a value Bool but when delete data user the key should delete
    """
    # This importan don't place carelessly
    # Must before addd_signup_to_db
    context.user_data[USER_SUCCESS_SIGNUP] = True
    # Insert data user to database
    add_signup_to_db(context)
    
    text = ("We have setting up your data\n <b>Succes</b> ✔️ ✔️")
    query_edit = update.callback_query
    query_edit.edit_message_text(text=text, parse_mode=ParseMode.HTML)
    
    # logging
    username = update.effective_user.username
    logger.info('Commit user data: %s', username)
    
    # back to top conversation
    main_menu(update, context)
    return END


def back_main(update: Update, context: CallbackContext):
    """Return to Top level conversation (back to Main Menu).
    Remove ReplyKeyboardRemove and inline button come
    from second level converstation (SIGNUP state) and 
    Clear data user in the persistance data
    """
    # Logger
    username = update.effective_user.username
    logger.info(
        'User {} Cancel from SIGNUP using keyboard costume'.format(username))
    context.user_data[USER_SUCCESS_SIGNUP] = False
    chat_id = update.effective_chat.id

    if update.callback_query:
        id_inline = update.callback_query.message.message_id
        context.bot.delete_message(chat_id=chat_id, message_id=id_inline)
    text = (f'You have <b>cancel SIGNUP</b> {e_cancel} converstation')
    context.bot.send_message(chat_id=chat_id,
                             text=text,
                             reply_markup=ReplyKeyboardRemove(selective=True)
                             )
    # Back to the first converstation
    main_menu(update, context)

    return END


def cancel_signup(update: Update, context: CallbackContext):
    """Exit from second conversation(signup)"""
    # logger
    user = update.effective_user
    logger.info('User {} Cancel from SIGNUP'.format(user.username))
    chat_id = update.effective_chat.id
    # Clear user indicate signup
    context.user_data[USER_SUCCESS_SIGNUP] = False
    user = update.message.from_user
    logger.error("Exit User = First name %s: message: %s", user.first_name,
                 update.message.text)
    text = (f"You have cancel {e_cancel} from /signup command or"
            "\ninline botton signup.\n"
            f"{e_command} /help")
    context.bot.send_message(chat_id=chat_id,
                             text=text,
                             reply_markup=ReplyKeyboardRemove())
    # Back to the first converstation
    main_menu(update, context)

    return END


def cancel_football(update: Update, context: CallbackContext):
    """"Exit from /football command. Top State"""

    user = update.effective_user

    text = (f"You have cancel/exit {e_cancel} from /football command.\n /help")
    if update.message:
        update.message.reply_text(text)
    else:
        query_edit = update.callback_query
        query_edit.edit_message_text(text=text)

    logger.info("User: {} EXIT from /football command".format(user.username))
    return END

def logs_main(update, context):
    """Log Errors caused by Updates."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.error)
    logger.error('Update "%s" caused error "%s"', update, context.error)

# Second level conversation (signup module)
conversation_signup = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(signup_module,
                             pattern='^' + str(SIGNUP) + '$',
                             pass_chat_data=True,
                             pass_user_data=True),
        CommandHandler('signup', signup_module,
                       Filters.private & Filters.command)
    ],
    states={
        USER_SIGNUP: [
            CallbackQueryHandler(signup_module,
                                 pattern='^' + str(SIGNUP) + '$'),
            CommandHandler('signup', signup_module, Filters.private)
        ],
        STACK_CONTACT:
        [MessageHandler(Filters.contact & Filters.private, contact_signup)],
        STACK_LOCATION:
        [MessageHandler(Filters.location & Filters.private, confirmation)],
        LOCATION_FINISH: [
            CallbackQueryHandler(insert_db,
                                 pattern='^' + str(INLINE_CONF) + '$')
        ]
    },
    fallbacks=[
        MessageHandler(Filters.all, cancel_signup),
        CommandHandler('cancel', cancel_signup, Filters.all),
        # back top level (Cancel signup)
        MessageHandler(
            Filters.regex(f'^(CANCEL) {e_cancel}$') & Filters.all, back_main),
        CallbackQueryHandler(back_main,
                             pattern='^' + str(f'CANCEL {e_cancel}') + '$')
    ],
    map_to_parent={
        # return Top level (SIGNUP_STATE state)
        END: SIGNUP_STATE
    },
    allow_reentry=False,
    # per_chat = False for allowed request from chat Eg.group to countinue in PM
    per_chat=False
    )
# Top level conversation (main_menu module)
conversation_main = ConversationHandler(
    entry_points=[CommandHandler('football', main_menu)],
    states={
        # After it will be SIGNUP_STATE state then back to main_menu.
        # so we need to conversation_signup for go to second state
        # if we remove conversation_signup when on msg_shedule (TODAY)
        # conversation will can't go to the second conversation
        FIRST: [
            conversation_signup,
            MessageHandler(Filters.text, main_menu),
            CallbackQueryHandler(main_menu,
                                 pattern='^' + str(TODAY) + '$',
                                 pass_groups=True),
            CallbackQueryHandler(main_menu,
                                 pattern='^' + str(SIGNUP) + '$',
                                 pass_chat_data=True,
                                 pass_user_data=True)
        ],
        # After /start, FIRST state will be stack on SIGNUP_STATE state
        # so we need to conversation_signup for go to the second state
        # if we remove conversation_signup when on entry_points
        # (/start) conversation will can't go to the second state
        SIGNUP_STATE: [
            conversation_signup,
            CallbackQueryHandler(msg_shedule, pattern='^' + str(TODAY) + '$'),
            CallbackQueryHandler(msg_shedule, pattern='^' + str(SIGNUP) + '$')
        ]
    },
    fallbacks=[
        MessageHandler(Filters.all, cancel_football),
        CommandHandler('cancel', cancel_football),
        CallbackQueryHandler(cancel_football,
                             pattern='^' + str(EXIT_FOOTBALL) + '$')
    ],
    allow_reentry=False,
    per_chat=False,
    persistent=True,
    name='control_Signup'
    # per_chat = False for allowed request from chat Eg.group to countinue in PM
    )