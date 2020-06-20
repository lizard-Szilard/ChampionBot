import os
import pathlib
import logging

# PTB
from telegram.ext import (ConversationHandler, CommandHandler,
                          MessageHandler, Filters, CallbackContext)

from telegram import (Update, ParseMode, ForceReply,
                      InlineKeyboardButton, InlineKeyboardMarkup)
# PTB helper/mention_html
from telegram.utils.helpers import mention_html

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
from jinja2 import (Environment,
                    FileSystemLoader)

from utills.permission import restricted_chat_class
                    

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class FeedBackUSer:
    """The main responsibility of this module is for /feedbackme command.
    This is for send feedback to the developer
    The feedback is write in feedback_user.txt file.
    """
    
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.__process_handler_feedback()

    @restricted_chat_class
    def feed_back(self, update: Update, context: CallbackContext):

        text_private = 'Send your <b>feedback</b>.\n/feedbackme'
        update.effective_user.send_message(text=text_private,
                                           reply_markup=ForceReply(selective=True))
        logger.info("User /feedbackme")
        return REQUEST_FEEDBACK

    def reciever_feedback(self, update: Update, context: CallbackContext):
        """If feedback user have less than 10 character will not allow.
        If user have a data in database we will write it in feedback.txt
        """
        reciever = update.message.text
        if len(reciever) <= 10:
            text_thml = ("Your sentence is less than 10 letter\n"
                         "I'm not allowed 🙅 \n\n"
                         "<b>lol</b> <b>lOl</b> <b>LoL</b> <b>LOL</b>"
                         "<b>LOL</b> <b>LOL</b> 😛 😛 😛 \n 💞 🌷 ")
            update.message.reply_html(text_thml)
            return END

        chat_id = update.effective_chat.id
        session = Session()
        text = 'My developer 💻 🤖 will review your feedback.\nThank for your Feedback 🌹'
        update.message.reply_text(text=text, parse_mode=ParseMode.HTML)

        user_information = session.query(UserData).filter_by(chat_id=chat_id).first()
        if user_information is not None:
            user_information_db = user_information
            folder_template = Environment(loader=FileSystemLoader('templates'))
            template = folder_template.get_template('feedback_user_template.txt')
            jinja_output = template.render(row_user_db=user_information_db, text_feedback=reciever)
        else:
            user_information_db = chat_id
            folder_template = Environment(loader=FileSystemLoader('templates'))
            template = folder_template.get_template('feedback_user_template.txt')
            jinja_output = template.render(row_user_db=user_information_db, text_feedback=reciever)
        
        # write to file
        # Location file Champion_league/feedback_user.txt
        with open('feedback_user.txt', 'a') as fu:
            fu.write(jinja_output)
            logger.info('User Feedback write file success')

        logger.info('User Feedback send text success')
        return END

        
    def fallbacks_feedback(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        text = ("You have cancel send feedback session.\n"
                " 🔑 /help")
        context.bot.send_message(chat_id=chat_id,
                                 text=text)
        logger.info('Exit user: class Feedback')
        return END
    
    def logs_feedback(self, update, context):
        """Log Errors caused by Updates."""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.error)
        logger.error('Update "%s" caused error "%s"', update, context.error)


    def __process_handler_feedback(self):

        conv_feedback = ConversationHandler(
            entry_points=[CommandHandler('feedbackme', self.feed_back)
                          ],
            states={
                REQUEST_FEEDBACK: [MessageHandler(Filters.reply & Filters.text & Filters.private & ~ Filters.command,
                                                  self.reciever_feedback),
                                   CommandHandler('cancel', self.fallbacks_feedback)
                                   ]
                    },
            fallbacks=[CommandHandler('cancel', self.fallbacks_feedback)
                       ],
            allow_reentry=True,
            per_chat=False,
            )
        self.dispatcher.add_handler(conv_feedback)