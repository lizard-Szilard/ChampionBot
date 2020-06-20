import os
import pathlib
import logging
# PTB
from telegram.ext import (ConversationHandler, CommandHandler,
                          MessageHandler, Filters, CallbackContext)
from telegram import (Update,ForceReply, InlineKeyboardButton, InlineKeyboardMarkup)
# Update and CallbackContext
from telegram import Update
from telegram.ext import CallbackContext
# For return State class LittleFeature
from utills.constants_cham import REQUEST_SEE, END
# For return State class Feedback
from utills.constants_cham import REQUEST_FEEDBACK
# View
from utills.uview import ViewUtills
from jobsView.view_main import ViewMain
from templates.not_format import TextChat
# Database
from pushdb.get_db import GetDatabase
from pushdb.models import Session, TeamSchedule, UserData

from datetime import datetime
import pytz
from jinja2 import (Environment, FileSystemLoader)
# Emoji
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

# TEST Restrict type chat
from utills.permission import restricted_chat

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

class SeeTeam:
    
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.__process_handler_Little()
        
    def see_team(self, update: Update, context: CallbackContext):
        """The main responsibility of this module is for /seeteam command.
        Chat type: Public
        View component: `ViewMain.message_seeteam` in `jobView/view_main.py`.
        """
        chat_id = update.effective_chat.id
        user_name = update.effective_user.username

        if not context.args:
            # if user not using command args
            text = (f'Send your team which you want to see schedule {e_ball}\n'
                    'You only can request 1️⃣ team ❗️ ❗️')
            context.bot.send_message(chat_id=chat_id, text=text,
                                     reply_markup=ForceReply(selective=True))
            logger.info('/seeteam User %s', user_name)
            return REQUEST_SEE
        else:
            try:
                look_at_db = ' '.join(context.args)
                request_user = str(look_at_db)
                logger.info('/seeteam: request %s', request_user)
                # Logger
                if len(request_user) < 3:
                    raise ValueError

                job_view = ViewMain(context.bot)
                job_view.message_seeteam(update, context,
                                         chat_user_id=chat_id,
                                         team_request=request_user)
                # Logging
                logger.info('User: %s Command.ags', user_name)
                return END
            except (ValueError):
                user_name = update.effective_user.username
                logger.info('Usser %s Request NOT FOUND: %s', user_name, request_user)

                text = (f"{e_ball} <b>NOT FOUND</b> 💁 💁\n"
                        "Sorry 🌷 📺, I didn't has a shedule of your request.\n"
                        "\nPerhaps you have a mistake when request a team.\n"
                        "\nEXAMPLE REQUEST:\n"
                        f"{e_command} /seeteam <b>arsenal</b> or send\n"
                        f"{e_command} /seeteam then send message for your favorite team")
                context.bot.send_message(chat_id=chat_id, text=text)
                # Logging
                logging.info('User: %s Command.args, NON FOUND',
                             user_name)
                return END

    def msg_seeteam(self, update :Update, context: CallbackContext):
        """The main responsibility of this module is for /seeteam command.
        Chat type: Public
        View component: `ViewMain.message_seeteam` in `jobView/view_main.py`.
        """
        # Logging
        user_name = update.message.from_user.username
        chat_user_id = update.effective_chat.id
        
        request_user = str(update.message.text)
        try:
            # Logger
            logger.info('/seeteam: request %s', request_user)
            if len(request_user) < 3:
                raise ValueError
            # send message
            job_view = ViewMain(context.bot)
            job_view.message_seeteam(update, context,
                                     chat_user_id=chat_user_id,
                                     team_request=request_user)
            # Logging
            logger.info('User: %s Command', user_name)
            return END
        except ValueError:
            user_name = update.effective_user.username
            logger.info('Usser %s Request NOT FOUND: %s', user_name, request_user)
            text = (f"{e_ball} <b>NOT FOUND</b> 💁 💁\n"
                    "Sorry 🌷 📺, I didn't has a shedule of your request.\n"
                    "\nPerhaps you have a mistake when request a team.\n"
                    "\nEXAMPLE REQUEST:\n"
                    f"{e_command} /seeteam <b>arsenal</b> or send\n"
                    f"{e_command} /seeteam then send message for your favorite team")
            # send meesage
            context.bot.send_message(chat_id=chat_user_id, text=text)
            # Logging
            logging.info('/seetam NON FOUND')

            return END
    
    def fallbacks_little(self, update: Update, context: CallbackContext):
        text = ("I don't know what your means is ❗️ ❗️ 💁\n"
                f"\n<b>help</b> {e_command} /help and\n"
                f"<b>see team</b> {e_command} /seeteam")
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        logger.info('Exit User: {} class LittleFeature'.format(update.effective_user.username))
        return END

    def logs_seeteam(self, update, context):
        """Log Errors caused by Updates."""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.error)
        logger.error('Update "%s" caused error "%s"', update, context.error)

    def __process_handler_Little(self):
        
        conv_see_team = ConversationHandler(
            entry_points=[CommandHandler('seeteam', self.see_team)
                          ],
            states={
                REQUEST_SEE: [MessageHandler(Filters.text & ~ Filters.command,
                                             self.msg_seeteam),
                              CommandHandler('cancel', self.fallbacks_little)
                              ]
                    },
            fallbacks=[CommandHandler('cancel', self.fallbacks_little, Filters.command),
                       MessageHandler(Filters.all, self.fallbacks_little)
                       ],
            allow_reentry=True
            )
        self.dispatcher.add_handler(conv_see_team)