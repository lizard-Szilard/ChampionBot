import logging
# PTB
from telegram.ext import CallbackContext
from telegram import (Update, InlineKeyboardButton,
                      InlineKeyboardMarkup, ReplyKeyboardRemove)
from utills.dict_in_memory import DATA_JOB
from utills.constants_cham import LIST_TEAM_FAV
# For return State class LittleFeature
from utills.constants_cham import END
# Emoji
from utills.constants_cham import emoji_all
from templates.not_format import TextChat

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

def start_me(update: Update, context: CallbackContext):
    """This callback for the /start command"""
    
    logger.info(f"List job.queue: {DATA_JOB}")
    a_user = update.effective_user
    type_chat = ['group', 'channel', 'supergroup']
    if update.effective_chat.type in type_chat:
        chat_id = update.effective_chat.id

        #Logger
        logger.info(f"Start GROUP User: {a_user.username}")

        url_signup = 'https://t.me/champion_update_id_bot?start='
        buttons_singup = [[InlineKeyboardButton("PM ME",
                                               url=url_signup)
                           ]]
        button_trial = InlineKeyboardMarkup(buttons_singup)
        bot_mention = context.bot.name
        text = (f"I'm not allow to signup in here 🤖 {e_ngece} \n"
                f"\n<b>PM</b> {bot_mention}\nif you want to this feature")
        context.bot.send_message(chat_id=chat_id,
                                 text=text,
                                 reply_markup=button_trial)
        return END
    chat_id = update.effective_chat.id
    text = ("🤖 OKAY. You Should send command\n"
            f"{e_command}/football or {e_command}/help")
    remove_keyborad = ReplyKeyboardRemove()
    context.bot.send_message(chat_id=chat_id,
                             text=text,
                             reply_markup=remove_keyborad)
    logger.info('The Command /start User: {}'.format(a_user.username))
    return END

def help_module(update, context):
    """Control Command Help"""

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=TextChat.text_help)
    return END