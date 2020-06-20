import logging
from jinja2 import (Environment, FileSystemLoader,)
# PTB
from telegram.ext import (ConversationHandler, CommandHandler,
                          MessageHandler, Filters, CallbackContext)
from telegram import (Update, ReplyKeyboardRemove)
from utills.constants_cham import END
# Persmission chat Eg. Group, channel and Supergroup
from utills.permission import restricted_chat
# Emoji
from utills.constants_cham import emoji_all
from utills.constants_cham import LIST_TEAM_FAV, USER_SUCCESS_SIGNUP
# Database
from pushdb.get_db import GetDatabase
from pushdb.models import Session, TeamSchedule, UserData
from datetime import datetime
import pytz

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
@restricted_chat
def my_fav(update: Update, context: CallbackContext):
    """This callback for the /listme command.
    Only list of home_team name
    Templates: listme.txt
    """
    chat_id = update.effective_chat.id
    user = update.effective_user
    session = Session()
    
    chat_user_db = [c.user_id for c in session.query(UserData).all()]
    if user.id not in chat_user_db:
        text = ("You haven't signup\n"
                "For <b>Signup</b> send "
                f"the {e_command} /football command")
        user.send_message(text=text)
        # Logger
        logger.info(f"User {user.username} nonLogin /listme callback: my_fav ")
        return END

    folder_template = Environment(loader=FileSystemLoader('templates'))
    template = folder_template.get_template('listme.txt')
    try:
        # Database Sqlalchemy
        query_team = session.query(UserData).join(TeamSchedule.user).\
            filter_by(chat_id=chat_id).first()
        list_team = [z for z in query_team.champion_league]
        a_list_team = list()
        for i in list_team:
            a_list_team.append(i.home_team)
        # Remove duplicate in list object
        team_fav = list(dict.fromkeys(a_list_team))
        text_template = template.render(row=team_fav, zone=query_team.tzinfo)
        user.send_message(text=text_template)

        logger.info(f"User: {user.username} have Team FAVORITE Callback: my_fav")
    except Exception as e:
        print(f"Error and Exception: {e}")
        text = (f"You haven't team favorite {e_ball}.\n"
                "\nFor add your team favorite use\n"
                f"command {e_command} /setfavorite"
                "\nExample:\n"
                f"❗️ {e_command} /setfavorite <b>arsenal</b>")
        context.bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"User: {user.username} don't have Team FAVORITE Callback: my_fav")
    return END