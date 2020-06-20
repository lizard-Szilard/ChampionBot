import logging
import os
# PTB
from telegram.ext import (ConversationHandler, CommandHandler,
                          MessageHandler, Filters, CallbackContext,
                          CallbackQueryHandler)
from telegram import (Update, ForceReply,
                      InlineKeyboardButton, InlineKeyboardMarkup,
                      ChatAction)

# Database Sqlalchemy
from pushdb.models import Session, UserData, TeamSchedule
# Persistance Key and Removal the job
from utills.constants_cham import (USER_SUCCESS_SIGNUP, LIST_TEAM_FAV, END)
# View
from jobsView.view_main import ViewMain

# Decorator Permission only PM
from utills.permission import restricted_chat
# Decorator chat.action
# Decorator Permission only signup
from utills.utils import send_action, restricted_non_signup

# Emoji
from utills.constants_cham import emoji_all
# Data of job reminder
from utills.dict_in_memory import DATA_JOB
e_command = emoji_all['command']
e_cancel = emoji_all['cancel']
e_location = emoji_all['location']
e_hand = emoji_all['hello']
e_ngece = emoji_all['ngece']
e_ball = emoji_all['ball']
e_phone = emoji_all['contact']
old_zone = emoji_all['timezone']
e_correct = emoji_all['correct']
e_qa = emoji_all['QA']

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# InlineKeyboardButton callback_dat
# State One
YES, NO  = 34506938, 65767903
# State Two
YES_DELETE = 742507


CALLBACK_TWO = "I AM_STATE_ONE"
CALLBACK_THREE = "Three STATE"

@restricted_non_signup
@restricted_chat
@send_action(ChatAction.UPLOAD_PHOTO)
@send_action(ChatAction.TYPING)
def request_delete_db(update: Update, context: CallbackContext):
    """The main responsibility of this module is for /deleteme command.
    It's will delete all data of a user.
    """
    user = update.effective_user
    file_name_photo = 'pic_user_privacy.jpg'
    with open(file_name_photo,'rb') as ph:
        text_caption = ("Maybe you are wonder why i'm provide this features"
                        "\nBecause......\n\n ☢️ ☢️ ")
        user.send_photo(photo=ph, caption=text_caption)

    text_YES = 'YES DELETE '
    text_NO = 'NO NO NO NO'
    button_YES = InlineKeyboardButton(text_YES, callback_data=str(YES))
    button_NO = InlineKeyboardButton(text_NO, callback_data=str(NO))

    button = [[button_YES], [button_NO]]
    reply_menu = InlineKeyboardMarkup(button)
    # Send message
    text = (f" 👻 💀 💀 💀 💀 💀 💀 💀 💀 💀 👻\n"
            f"\nAre you <b>sure</b> to <b>delete</b> data on <b>my database</b> {e_qa} {e_qa}"
            f"\n"
            f"\n<b>NOTE:</b>\n"
            f"If you delete your data, I will <b>not reminder about shedule</b> of"
            " your team favoritmu and delete all your data ❗️ ❗️ "
            )
    user.send_message(text=text, reply_markup=reply_menu)

    return CALLBACK_TWO

def present_data(update: Update, context: CallbackContext):
    """For presentation data to the user."""
    
    text_sure = "Sure Delete"
    text_no = "NO NO NO"
    button_YES = InlineKeyboardButton(text_sure, callback_data=str(YES_DELETE))
    button_NO = InlineKeyboardButton(text_no, callback_data=str(NO))
    
    button = [[button_YES], [button_NO]]
    button_markup = InlineKeyboardMarkup(button)

    sendMessgae = ViewMain()
    sendMessgae.view_represent_data(update, context, reply_markup=button_markup)
    return CALLBACK_THREE

def delete_data_true(update: Update, context: CallbackContext):
    """The data user is purging then allow user to signup and disallow
    all feature that needed to signup.
    We use 'del' method instead assignment 'True' becuase we use 
    metode 'dict.get' for identiify user signup or not.
    The 'dict.get' methode will 'False' when item not exist and
    vice versa"""

    user = update.effective_user
    chat = update.effective_chat
    
    try:
        # This also remove job reminder for all team favorite
        # Exception will not remove job because user not have 
        # team faorite
        session = Session()
        msg_info = "Delete using join {}".format(user.username)
        logger.info(msg_info)
        delete_data = session.query(UserData).\
            join(TeamSchedule.user).filter_by(user_id=user.id).first()
        session.delete(delete_data)
        session.commit()
        
        # Purge the job.queue
        job_dict = DATA_JOB[chat.id]
        for key_team, value_job_team in job_dict.items():
            logger.info(f'Remove JOB: {key_team} Schedule')
            for job in value_job_team:
                job.schedule_removal()
        # Delete all job
        del DATA_JOB[chat.id]
    except Exception:
        # User haven't team favorite
        msg_info = "Delete at Exception {} User haven't not team favorite".format(user.username)
        logger.info(msg_info)
        delete_data = session.query(UserData).filter_by(user_id=user.id).first()
        session.delete(delete_data)
        session.commit()
    finally:
        # Delete all data on Persistance
        context.user_data.clear()
        context.chat_data.clear()
        logger.info("Final: Send Message 'Purge Finish' {}".format(user.username))
        text = " 🆗 😞 Purge data finish 😞 🆗 "
        inline = update.callback_query
        inline.edit_message_text(text=text)
    
    return END

def cancel_delete_data_user(update: Update, context: CallbackContext):
    user = update.effective_user
    inline = update.callback_query
    if inline:
        text = "Oke ❗️ Good Choices ❗️ ✔ ✔️ 😄 😄 "
        inline.edit_message_text(text=text)
    else:
        text = "Sorry you have exit in this session"
        user.send_message(text)
    return END 

def logs_delete_request(update, context):
    """Log Errors caused by Updates."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.error)
    logger.error('Update "%s" caused error "%s"', update, context.error)
    return


# pattren CallbackQueryHandler
pattren_two = '^' + str(YES) + '$'
pattren_three = '^' + str(YES_DELETE) + '$'
pattren_no = '^' + str(NO) + '$'
# Conversation Handler
conv_request_delete = ConversationHandler(
    entry_points=[CommandHandler('deleteme', request_delete_db)
                  ],
    states={
        CALLBACK_TWO :[CallbackQueryHandler(present_data,
                                            pattern=pattren_two)
                       ],
        CALLBACK_THREE: [CallbackQueryHandler(delete_data_true,
                                              pattern=pattren_three)]
            },
    fallbacks=[CallbackQueryHandler(cancel_delete_data_user, pattern=pattren_no),
               MessageHandler(Filters.all, cancel_delete_data_user),
               CommandHandler('cancel', cancel_delete_data_user)
               ],
    allow_reentry=False,
    persistent=True,
    name='control_delete_user_data')