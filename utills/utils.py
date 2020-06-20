import logging
from utills.uview import ViewUtills
from datetime import datetime
from utills.constants_cham import (USER_SUCCESS_SIGNUP, END)
from telegram import Update
from telegram.utils.helpers import mention_html
from telegram.ext import CallbackContext

# Test
import shelve
from pickle import HIGHEST_PROTOCOL
import pickle

from jinja2 import (Environment,
                    FileSystemLoader)
from jinja2 import exceptions as exp

#Decorator
from functools import wraps
# Database
from pushdb.models import (Session, TeamSchedule, UserData)

from utills.constants_cham import emoji_all
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
    level=logging.info)
logger = logging.getLogger(__name__)


def get_logger():
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    return logger

def add_handlers(dispatcher, handlers):
    for handler in handlers:
        dispatcher.add_handler(handler)


def send_action(action):
    """Sends `action` while processing func command."""
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    return decorator

def restricted_non_signup(func):
    """
    The main responsibility of this module for not
    allowd who not signup
    """
    @wraps(func)
    def wrapped_non_signup(update: Update, context: CallbackContext, *args, **kwargs):
        logger.info('Wrape for permission_non_signup')
        session = Session()
        chat_id_from_out = update.effective_chat.id
        iduser_from_db = [r.chat_id for r in session.query(UserData).all()]
        print(iduser_from_db)

        if chat_id_from_out not in iduser_from_db:
            user = update.effective_user
            text_restricted = ("I don't have your data ❗️ ❗️ 😞 \n"
                               f"\nMay you want to signup {e_qa} {e_qa}\n"
                               f"\nSend to me the \n{e_command} /football command to signup"
                               )
            user.send_message(text=text_restricted)
            logger.info(f"Unauthorized access denied for: {user.username}")
            return END
        return func(update, context, *args, **kwargs)
    return wrapped_non_signup

def dict_init_context(team, user, addional):
    """The main responsibility of this handler is for send message by the job.queue.
    Controller: `notif_for_job` in controller/job_main.py`
    Template: job_text.txt
    """
    add_dict = {'zone_name': user.tzinfo,
                'match_date': addional
                }
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('job_text.txt')
    result_msg = template.render(row=team, dict_row=add_dict)
    logger.info("Make CONTEXT for job_dict for user: {}.\n"
                "Callback: dict_init_context".format(user.username))
    return {'chat_id': user.chat_id,
            'send_text': result_msg
            }

def remove_duplicate_list(a_list: list, addional_data=None):
    """
    Remove ducplicate value in list.
    Args:
        a_lits: list object contain duplicate
        addional_data: data will add to list object
    return: list without duplicate
    """
    logger.info(f"remove_duplicate_list")
    if addional_data is None:
        result = list(dict.fromkeys(a_list))
    else:
        a_list.append(addional_data)
        result = list(dict.fromkeys(a_list))
    logger.info(f"remove_duplicate_list {result}")
    return result