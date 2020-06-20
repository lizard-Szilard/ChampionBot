import logging
# Get database
from pushdb.models import Session, UserData
from pushdb.add_update import update_send_to_db
from telegram import (Message, Update)
# Telegram markup
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton)
# Telegra.ext Handler
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, 
                          Filters, MessageHandler)
# Telegram helper
from telegram.utils.helpers import mention_html
from timezonefinder import TimezoneFinder
# Callback_data Callback Query
from utills.constants_cham import (CONFIRM_CHANGE_DATA,
                                   END, NO_CHANGE_DATA,
                                   YES_CHANGE_DATA,
                                   emoji_all)
# key context.user_data in signup
from utills.constants_cham import (DATA_CONTACT, USER_SUCCESS_SIGNUP,
                                   DATA_LATITUDE,DATA_LONGITUDE,
                                   TZINFO, USER_ID,
                                   CHAT_ID, NEW_CONTACT)
# Permisiion chat Eg. group or channel
from utills.permission import restricted_chat
from utills.utils import restricted_non_signup

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# Emoji
old_zone = emoji_all['timezone']
old_phone = emoji_all['contact']
e_command = emoji_all['command']
e_cancel = emoji_all['cancel']
e_location = emoji_all['location']
e_hand = emoji_all['hello']

# State return
FIRST_DATA = 1020
SEND_LOC = 1021
CONFIRM = 1023
INSERT_DB = 1024

@restricted_non_signup
@restricted_chat
def change_data(update: Update, context: CallbackContext):
    """The main responsibility of this method is for /changeme command, it's for change data
    of user e.g. contact and location.
    We get contact and location data user from persistance PTB.
    Chat type: Private
    """

    user = update.effective_user
    logger.info(f'Module: change_data db User: {user.username}')

    # Send message in PM when user request in public chat
    LIST_OF_TYPE_CHAT = ['group', 'channel', 'supergroup']
    if update.effective_chat.type in LIST_OF_TYPE_CHAT:
        text_private = ("Send command 🔑 /changeme for update your data.")
        user.send_message(text=text_private)

    button_yes = InlineKeyboardButton(text='YES SURE',
                                      callback_data=str(YES_CHANGE_DATA))
    button_no = InlineKeyboardButton(text='NO',
                                     callback_data=str(NO_CHANGE_DATA))
    button_all = [[button_yes], [button_no]]
    button = InlineKeyboardMarkup(button_all)

    timezone = context.user_data[TZINFO]
    phone_number = context.user_data[DATA_CONTACT]
    # emoji
    q, a, e = emoji_all['QA'], emoji_all['QA'], emoji_all['QA']
    text_privat = (f"{e_hand},  Are you <b>sure</b> to change your"
                   f" data {q} {a} {e}\n"
                   "\n<b>YOUR DATA:</b> 📕\n"
                   f"{old_zone}\n"
                   f"TIMEZONE:  <b>{timezone}</b>\n"
                   f"{old_phone}\n"
                   f"PHONE NUMBER:  <b>{phone_number}</b>"
                   )
    user.send_message(text=text_privat, reply_markup=button)
    return FIRST_DATA

def send_contact(update: Update, context: CallbackContext):
    user = update.effective_user
    # logger
    msg_info = f"Change/Update contact User: {user.full_name}"
    logger.info(msg_info)
    msg_id = update.callback_query.message.message_id
    context.bot.delete_message(chat_id=update.effective_chat.id,
                               message_id=msg_id)
    text = (
        f"Send your phone number with keyboard custome {old_phone}.\n"
        "\nIf you send with other method <b>Eg. message text or command</b>"
        f" you will <b>CANCEL</b> {e_cancel} Update session ❗️ ❗️\n"
        "\nYou can cancel using keyboard or\n"
        f" {e_command} /cancel command"
        )
    button_text_contact = f"CONTACT {old_phone}"
    cancel_button = f"CANCEL {e_cancel}"
    back_keyboard = KeyboardButton(text=cancel_button)
    contact_keyboard = KeyboardButton(text=button_text_contact,
                                      request_contact=True)
    custom_keyboard = [[contact_keyboard], [back_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    context.bot.send_message(chat_id=update.effective_chat.id, text=text,
                             reply_markup=reply_markup)
    return SEND_LOC

def send_location(update: Update, context: CallbackContext):
    """Difference with (control_main.py) is either 
    DAT_CONTACT and NEW_CONTACT
    """

    contact = update.message.contact
    # Constant NEW_CONTACT variable
    context.user_data[NEW_CONTACT] = str(contact.phone_number)

    if len(contact.first_name) == 0:
        context.user_data['name_contact'] = str(contact.last_name)
    else:
        context.user_data['name_contact'] = str(contact.first_name)

    location_button = f"LOCATION {e_location}"
    cancel_button = f"CANCEL {e_cancel}"
    back_keyboard = KeyboardButton(text=cancel_button)
    location_keyboard = KeyboardButton(text=location_button, request_location=True)
    custom_keyboard = [[location_keyboard], [back_keyboard]]

    text = (
        "Send your location using custome keyboard"
        f" {e_location} {e_location} {e_location}\n"
        f"\nSend your location correctly ✔️\n"
        f"it's for setting your <b>TIMEZONE</b> {e_location}\n"
        "\nIf you send with other method <b>Eg. message text or command</b>"
        f" you will\n <b>CANCEL</b> ❗️ {e_cancel}"
        " this Update seesion")
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             reply_markup=reply_markup)
    logger.info("Update CONTACT of %s: Number: %s", contact.first_name,
                contact.phone_number)
    return CONFIRM


def confirmation_update(update: Update, context: CallbackContext):
    """The main responsibility of this handler is for the button "YES Confirmation.
    Constanta variable from `utills/constants.py 
    Data will insert to database.
    username: update.message.from_user.username str
    LOCATION: float
    DATA_CONTACT phone_number: string
    USER_ID: update.effective_user.id or telegram.user.id int
    CHAT_ID: effective._chat.id int
    Difference with (control_main.py) is either 
    DAT_CONTACT and NEW_CONTACT
    """
    user = update.effective_user

    context.user_data[CHAT_ID] = int(update.effective_chat.id)
    context.user_data[USER_ID] = int(update.effective_user.id)
    # maybe it will error when update database to specifict user and
    # will error when job_pickle not in context manager open
    user_location = update.message.location
    context.user_data[DATA_LATITUDE] = float(user_location.latitude)
    context.user_data[DATA_LONGITUDE] = float(user_location.longitude)

    logger.info("LOCATION: %f / %f", user_location.latitude, user_location.longitude)

    # Convert latitude and longitude to tzinfo
    latitude = context.user_data[DATA_LATITUDE]
    longitude = context.user_data[DATA_LONGITUDE]
    tf = TimezoneFinder()
    tzinfo = tf.timezone_at(lng=longitude, lat=latitude)
    context.user_data[TZINFO] = tzinfo
    context.user_data['username'] = update.message.from_user.username

    # send message
    chat_id = update.effective_chat.id
    text_one = "👀  👀\n 👀  👀"
    context.bot.send_message(chat_id=chat_id, text=text_one,
                             reply_markup=ReplyKeyboardRemove(selective=True))
    button_confirm = InlineKeyboardButton( "YES confirmation",
                                          callback_data=str(CONFIRM_CHANGE_DATA))
    button_cancel = InlineKeyboardButton("CANCEL",
                                         callback_data=str(NO_CHANGE_DATA))
    buttons = [[button_confirm], [button_cancel]]
    button_send = InlineKeyboardMarkup(buttons)
    # Database Sqlalchemy
    session = Session()
    db_user = session.query(UserData).filter_by(user_id=user.id).first()
    #logger
    msg_info = ("Confirm data to change User: {}".format(user.full_name))
    logger.info(msg_info)
    # Send message
    timezone = context.user_data[TZINFO]
    phone_number = context.user_data[DATA_CONTACT]
    text_confirm = ("Your data..!! 📖 📖\n"
                    "\n<b>New Data:</b> 🆕 \n"
                    "⌚️\n"
                    f"Timezone: <b>{timezone}</b>.\n"
                    "📱\n"
                    f"Phone number: <b>{phone_number}</b>.\n"
                    "\n<b>Old Data:</b> 📕\n"
                    f"{old_zone}\n"
                    f"Timezone: <b>{db_user.tzinfo}</b>\n"
                    f"{old_phone}\n"
                    f"Phone number: <b>{db_user.contact}</b>"
                    )
    user.send_message(text=text_confirm, reply_markup=button_send)
    logger.info("User {} in confirmation".format(user.username))
    return INSERT_DB

def update_to_db(update: Update, context: CallbackContext):
    """Update data in database"""
    # update to database
    result = update_send_to_db(context)
    text = ("We have update your data.\n<b>Succes</b> ✔️ 🔐")
    if result is False:
        text = ("LOL Lol lol.\n I have problem about my database 😞 \n"
                "Your update data failed")
    query_edit = update.callback_query
    query_edit.edit_message_text(text=text)
    # logging
    username = update.effective_user.username
    logger.info('Commit data to Update User: %s', username)
    return END

def cancel_changed(update: Update, context: CallbackContext):
    """A user cancel update data and we represent the data"""
    user = update.effective_user
    # Database Sqlalchemy
    session = Session()
    db_user = session.query(UserData).filter_by(user_id=user.id).first()
    #logger
    user = update.effective_user
    msg_info = (f"Module cancel_changed cancel update data a User: {user.full_name}")
    logger.info(msg_info)
    # send message
    text = (f"Your data <b>not change</b> {e_cancel} \n"
            "\n<b>Your Data:</b> 📕\n"
            f"{old_zone}\n"
            f"Timezone: <b>{db_user.tzinfo}</b>\n"
            f"{old_phone}\n"
            f"Phone number: <b>{db_user.contact}</b>\n"
            )
    # if a user cancel using inline button
    if update.callback_query:
        query_edit = update.callback_query
        query_edit.edit_message_text(text=text)
        return END
    user.send_message(text=text, reply_markup=ReplyKeyboardRemove(selective=True))
    return END

def logs_update_delete(update, context):
    """Log Errors caused by Updates."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.error)
    logger.error('Update "%s" caused error "%s"', update, context.error)

# State
# Callback query Handler
parram_first_data = '^' + str(YES_CHANGE_DATA) + '$'
parram_cancel = '^' + str(NO_CHANGE_DATA) + '$'
parram_insert_db = '^' + str(CONFIRM_CHANGE_DATA) + '$'
# Filter regex contact and location
# Not used because will no work
# contact = Filters.regex('^(CONTACT)$')
# location = Filters.regex('^(LOCATION)$')
# regex_cancel = "CANCEL {}".format(e_cancel)
conv_change_data = ConversationHandler(
    entry_points=[CommandHandler('changeme', change_data)],
    states={
        FIRST_DATA:
        [CallbackQueryHandler(send_contact, pattern=parram_first_data)],
        SEND_LOC: [MessageHandler(Filters.contact, send_location)],
        CONFIRM: [MessageHandler(Filters.location, confirmation_update)],
        INSERT_DB: [
            CallbackQueryHandler(update_to_db, pattern=parram_insert_db),
            CallbackQueryHandler(cancel_changed, pattern=parram_cancel)
        ]
    },
    fallbacks=[# we can't combane filter.regex with filter.text/command
        MessageHandler(
            Filters.all & Filters.text & Filters.command, cancel_changed),
        MessageHandler(
            Filters.regex(f'^(CANCEL {e_cancel})$'), cancel_changed),
        CallbackQueryHandler(cancel_changed, pattern=parram_cancel)
    ],
    allow_reentry=False,
    per_chat=False,
    persistent=True,
    name='Control_change_data'
    )