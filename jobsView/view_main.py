import json
import logging
import os
from config import DATABASE_URL
from datetime import datetime

# Databse psycopg2
from pushdb.get_db import GetDatabase
# Database Sqlalchemy
from pushdb.models import Session, TeamSchedule, UserData
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      ReplyKeyboardMarkup, Update)
from templates.not_format import TextChat
# Emoji
from utills.constants_cham import CLUB, USER_SUCCESS_SIGNUP, emoji_all
from utills.ucallendar import TimeUtils
from utills.uview import ViewUtills

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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# The text to a user
textchat = TextChat()

class ViewMain:
    """The main responsibility of this class is 'sending messages of each state in bot'.
    and also 'formatting of messages', etc.
    All method have (update and context) except text_formater method
    Args:
        `bot (context.bot)` default `None`
    """
    def __init__(self, bot=None):
        self.bot = bot
        # self.msg_sender = MessageSender(bot=bot)

    def main_menu_view(self, update, context, markup_nonsignup, markup_signup):
        """The main responsibility of this method for the view component.
        Controller: `main_menu` handler in controller/control_main.py,
        Template: None
        Text : `TextChat.text_has_signuo` in tempfiles/non_format.py
               `TextChat.main_menu_text`
        Chat type: private
        """
        if context.user_data.get(USER_SUCCESS_SIGNUP):
            print(context.user_data[USER_SUCCESS_SIGNUP])
            # A user has signup
            text = textchat.text_has_signup
            reply_markup_start = markup_signup
        else:
            # hasn't signup yet
            text = textchat.main_menu_text
            reply_markup_start = markup_nonsignup

        # This will send to private user
        update.effective_user.send_message(text=text, reply_markup=reply_markup_start)

    def message_everyday(self, update, context,
                         reply_menu,
                         str_tdate,
                         timezone_user):
        """The main responsibility of this method for the view component.
        Controller: 'ControlMain.msg_schedule' handler in controller/control_main.py,
        Template: hello.txt
        Text : Directly database
        Args:
            reply_menu: Inline button non sign up or has sign up
            str_tdate: date today have convert to timezone user or default timzone
            timezone_user (str): timezone user, default asia/jakarta
        TODO: Change the ViewUtills module to directly use jinja2
        """
        view_formatter = ViewUtills(dir_temp='templates', file_template='hello.txt')
        getdb = GetDatabase(DATABASE_URL)
        # Get schedule
        schedule_today = getdb.get_from_date(datetime_db=str_tdate, zone_time=timezone_user)
        if schedule_today is not None:
            text = view_formatter.view_unpackage(data_unpackage=schedule_today,
                                                 additonal_dict=timezone_user)
            update.callback_query.edit_message_text(text=text, reply_markup=reply_menu)
        else:
            text = (f" 😞 😞 😞 <b>SORRY</b> 😞 😞 😞\n"
                    f"\nWe not have schedule today\n"
                    f"{e_ball} <b>{str_tdate}</b>  ❗️")
            update.callback_query.edit_message_text(text=text, reply_markup=reply_menu)
        logger.info("Module View: msg_schedule SCHEDULE TODAY")

    def check_in_db_view(self, update, context, chat_id, reply_markup):
        """The main responsibility of this method for the view component.
        Controller: 'ControlSetFavorite.setmyteam' handler in controller/control_setfavorite.py,
        """
        team = context.chat_data[CLUB]
        text = (f"I have found \n<b>{team}</b>\nCluab your favorite team.\n"
                "Click 🆗 <b>YES Reminder</b> 🆗 if you want to reminder you"
                " favorite team.\n"
                f"\nYou can {e_cancel} <b>CANCEL</b> {e_cancel}\n")
        context.bot.send_message(chat_id=chat_id, text=text,
                                 reply_markup=reply_markup)

    def message_seeteam(self, update, context, chat_user_id, team_request):
        """The main responsibility of this module is for view component'.
        Controller: `SeeTeam.see_team` handler in `controller/control_seeteam.py`,
        Template: see_team.txt
        Text : Database SqlAlchemy
        Chat type: public
        """
        # Database connection
        db = GetDatabase(DATABASE_URL)
        session = Session()
        formatter = ViewUtills(dir_temp='templates', file_template='see_team.txt')
        # Request user
        request_user = team_request.strip().lower()
        have_signup = [r.chat_id for r in session.query(UserData.chat_id).all()]

        if chat_user_id in have_signup:
            # Data user (tzinfo)
            user_db = session.query(UserData).\
                filter_by(chat_id=chat_user_id).first()
            # psycopg2 get data team
            db_result = db.select_seeteam(team_club=request_user, zone=user_db.tzinfo)

            if db_result is not None:
                text = formatter.view_unpackage(data_unpackage=db_result,
                                                additonal_dict=user_db.tzinfo)
            else:
                text = (f" 😞 😞 😞 <b>SORRY</b> 😞 😞 😞\n"
                        f"\nWe not have schedule for\n"
                        f"{e_ball} <b>{request_user}</b> team ❗️")
            context.bot.send_message(chat_id=chat_user_id, text=text)
        else:
            default_zone = 'Asia/Jakarta'
            db_result = db.select_seeteam(team_club=request_user, zone=default_zone)
            if db_result is not None:
                text = formatter.view_unpackage(data_unpackage=db_result,
                                                additonal_dict=default_zone)
            else:
                text = (f" 😞 😞 😞 <b>SORRY</b> 😞 😞 😞"
                        f" We not have schedule for {e_ball}"
                        f" <b>{request_user}</b> team {e_ball}")
            context.bot.send_message(chat_id=chat_user_id, text=text)
        logger.info(("View: For /seeteam SeeTeam class"))

    def view_represent_data(self, update, context, reply_markup):
        """The main responsibility of this module is for view component'.
        Controller: `present_data` handler in `controller/control_delete.py`,
        Template: delete_user.txt
        Text : Database Sqlalchemy
        Chat type: private
        All method have (update and context) except text_formater method
        NOTE: Remember when a user not have a team favorite it will can't to do join
        """
        user = update.effective_user
        # Database
        session = Session()
        query_team = session.query(UserData).join(TeamSchedule.user).\
            filter_by(user_id=user.id).first()

        if query_team is None:
            query_team = session.query(UserData).\
                filter_by(user_id=user.id).first()

        # Jinja View
        formatter = ViewUtills(dir_temp='templates', file_template='delete_user.txt')
        text = formatter.view_unpackage(data_unpackage=query_team)
        # Send messgae
        query_inline = update.callback_query
        query_inline.edit_message_text(text=text, reply_markup=reply_markup)