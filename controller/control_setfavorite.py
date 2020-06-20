import json
import os
import logging
from config import DATABASE_URL
from datetime import timedelta
from telegram import (Update, InlineKeyboardMarkup, InlineQuery,
                      KeyboardButton, InlineKeyboardButton, ReplyMarkup, ForceReply)
from telegram.ext import (CommandHandler, CallbackQueryHandler,
                          ConversationHandler, MessageHandler,
                          CallbackContext, Filters, StringCommandHandler)
# from control_main import ControlMain
from jobsView.view_main import ViewMain
from utills.constants_cham import (CLUB, REMIND, CHECK, VERIFICATION,
                                   YES, CANCEL_FAV, AGAIN, END, VERI)
# Key user_data
from utills.constants_cham import (USER_SUCCESS_SIGNUP, LIST_TEAM_FAV)
# Database Sqlalchemy and Psycopg
from pushdb.get_db import GetDatabase
from pushdb.models import Session, UserData, TeamSchedule
from pushdb.persist_pickle import save_jobs
from pushdb.add_update import add_to_fav
# View
from jobsView.view_main import ViewMain
from controller.jobs_main import job_from_login

# Emoji
from utills.constants_cham import emoji_all
from utills.utils import remove_duplicate_list
# Permission chat group etc.
from utills.permission import restricted_chat_class

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
e_sad = emoji_all['sad']
from utills.dict_in_memory import DATA_JOB

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class ControlSetFavorite:
    """
    The main responsibility of this class is '/setfavorite' command.
    The /setfavorite command is for change set favorite a user team and add to databse.
    User non sign up don't allowed.
    A user maximum have 5 team favorite.
    """
    
    # For view component
    job_view = ViewMain()

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.__process_handler_login()
        
    @restricted_chat_class
    def setmyteam(self, update: Update, context: CallbackContext):

        self.chat_id = update.effective_chat.id
        user_name = update.effective_user.username
        
        # addional text for permission chat. This will send to text private
        type_chat = update.effective_chat.type
        LIST_OF_TYPE_CHAT = ['group', 'channel', 'supergroup']
        if type_chat in LIST_OF_TYPE_CHAT:
            # send to private messgae
            text_private = (f"To use {e_command} /setfavorite command you"
                            " <b>should SIGNUP</b>")
            update.effective_user.send_message(text_private)
            return END
        # If a user not signup
        if not context.user_data.get(USER_SUCCESS_SIGNUP):
            text = (" 😄 😄, You can't use this feature cause you haven't SIGUNP"
                    " 🚫 🚫")
            update.message.reply_text(text)
            return END
        # List team favroite a user max 5 team
        if context.user_data.get(LIST_TEAM_FAV) and len(context.user_data[LIST_TEAM_FAV]) == 5:
                update.message.reply_text("You have been have 5 team in your list favorite,\n "
                                          "\nI'm not allowed ❗️ ❗️")
                logger.info(f"User: {user_name}. Total Team favorite = 5:\n"
                            f"{context.user_data[LIST_TEAM_FAV]}")
                return END
        # if user use command
        if not context.args:
            text = (f" ⚽️ ⚽️ What your favorite team schedule 🗒 📆 🗓"
                    f" would to remind {e_qa} {e_qa}"
                    )
            update.message.reply_text(text=text, reply_markup=ForceReply(selective=True))
            logger.info('User %s /setfavorite INSERT TEXT', user_name)
            return CHECK

        # If the user use command args feature
        # Context.args block
        buttom_YES = 'YES Reminer'
        button_NO = 'Set Favorite team and END conversation'
        button = [
            [InlineKeyboardButton(buttom_YES, callback_data=str(YES))],
            [InlineKeyboardButton(button_NO, callback_data=str(CANCEL_FAV))]
                  ]
        reply_menu = InlineKeyboardMarkup(button)

        try:
            team_fav = ' '.join(context.args)
            request_user = str(team_fav)

            # Logger
            user_name = update.effective_user.username
            logger.info('User %s Command.args: %s', user_name, team_fav)

            if len(request_user) < 3:
                raise ValueError
            # Check if request exist in the database
            db = GetDatabase(DATABASE_URL)
            db_result = db.select_team(request_user.strip().lower())
            if db_result is None:
                raise ValueError
            if len(db_result) is not 0:
                team = db_result[0][4] # The same as db_result.home_team
                context.chat_data[CLUB] = team

                # Check if request user already in list favorite
                if context.user_data.get(LIST_TEAM_FAV) and team in context.user_data[LIST_TEAM_FAV]:
                    text_have_team = (f"Your {team} team favorite already in your list\n"
                                      "/listme command to see your list team")
                    update.message.reply_text(text_have_team)

                    return END
                else:
                    # Send message user have not team fav                
                    self.job_view.check_in_db_view(update, context,
                                                   chat_id=self.chat_id,
                                                   reply_markup=reply_menu)
                # Logging
                logging.info('User: %s Command.ags, Chose team: %s', user_name, team)
                return VERIFICATION
            else:
                raise ValueError
        except ValueError:
            text = (f"{e_ball} <b>NOT FOUND</b> 💁 💁\n"
                    "Sorry 🌷 📺, I didn't have a shedule of your request.\n"
                    "\nPerhaps you have a mistake when request a team.\n"
                    "\nEXAMPLE REQUEST:\n"
                    f"{e_command} /seeteam <b>arsenal</b> or send\n"
                    f"{e_command} /seeteam then send message for your favorite team")
            context.bot.send_message(chat_id=self.chat_id, text=text)

            logging.info(f'User:{user_name} Command.args, NON FOUND team {team_fav}')
            return END

    def check_in_db(self, update: Update, context: CallbackContext):
        """check whether request user matches with database and ask add to favorite a team"""
        # Logging
        user_name = update.message.from_user.username
        logging.info('User: %s on state CHECK', user_name)

        buttom_YES = 'YES Reminer'
        button_NO = 'CANCEL and END conversation'
        button = [
            [InlineKeyboardButton(buttom_YES, callback_data=str(YES))],
            [InlineKeyboardButton(button_NO, callback_data=str(CANCEL_FAV))]
                  ]
        reply_menu = InlineKeyboardMarkup(button)
        # A get request from a user
        request_user = str(update.message.text)
        try:
            if len(request_user) < 4:
                raise ValueError
            # check in database
            db = GetDatabase(DATABASE_URL)
            db_result = db.select_team(request_user.strip().lower())            
            if db_result is None:
                raise ValueError
            
            if 0 != len(db_result):
                team = db_result[0][4] # The same as db_result.home_team
                context.chat_data[CLUB] = team
                # Check if request user already in list favorite
                if context.user_data.get(LIST_TEAM_FAV) and team in context.user_data[LIST_TEAM_FAV]:
                    text_have_team = (f"Your {team} team favorite already in your list\n"
                                      "/listme command to see your list team")
                    update.message.reply_text(text_have_team)
                    return END
                else:
                    # Send message user have not team fav                
                    self.job_view.check_in_db_view(update, context,
                                                   chat_id=self.chat_id,
                                                   reply_markup=reply_menu)
                logging.info('User: %s on state CHECK, Chose team: %s', user_name, team)
                return VERIFICATION
            else:
                raise ValueError
        except ValueError:
            print('Not Found team: %s', request_user)
            logger.info('Usser %s Request NOT FOUND: %s', user_name, request_user)

            text = (f"{e_ball} <b>NOT FOUND</b> 💁 💁\n"
                    "Sorry 🌷 📺, I didn't have a shedule of your request.\n"
                    "\nPerhaps you have a mistake when request a team.\n"
                    "\nEXAMPLE REQUEST:\n"
                    f"{e_command} /seeteam <b>arsenal</b> or send\n"
                    f"{e_command} /seeteam then send message for your favorite team")
            context.bot.send_message(chat_id=self.chat_id, text=text)

            logging.info('User: %s on state CHECK, NON FOUND',
                         user_name)
            return END

    def verification_spam(self, update: Update, context: CallbackContext):

        team = context.chat_data[CLUB]
        user_name = update.effective_user.username
        logging.info('User: %s on state: Verification, Team: %s',
                     user_name, team)
        text = f"You will add {e_ball} <b>{team}</b> {e_ball} or you can cancel"

        text_verification = 'Verification'
        button_verification = InlineKeyboardButton(text_verification, callback_data=str(VERI))
        text_cancel = 'CANCEL and END Conversation'
        button_cancel = InlineKeyboardButton(text_cancel, callback_data=str(CANCEL_FAV))

        button = [[button_verification], [button_cancel]]
        keyboard_menu = InlineKeyboardMarkup(button)

        update.callback_query.edit_message_text(text=text,reply_markup=keyboard_menu)

        return REMIND

    def insert_to_remind(self, update: Update, context: CallbackContext):
        """The main of this fucnion is inser data to the database table user and
        add job.queue
        """
        team_register = context.chat_data[CLUB]
        # if user haven't team favorite yet
        if not context.user_data.get(LIST_TEAM_FAV):
            context.user_data[LIST_TEAM_FAV] = list()
        # add to database favorite_team
        result = add_to_fav(favorite=team_register, chat_id=update.effective_chat.id)
        
        if result is True:
            # Send "Schedule team" to job_queue
            has_job = job_from_login(update, context)
            # Updating list team favorite max 5 team
            chat_id = update.effective_chat.id
            if has_job is True:
                job_data = DATA_JOB[chat_id]
                for k in job_data.keys():
                    context.user_data[LIST_TEAM_FAV].append(k)
                    duplicate = context.user_data[LIST_TEAM_FAV]
                    context.user_data[LIST_TEAM_FAV] = remove_duplicate_list(a_list=duplicate)

                if f'CANCEL {e_cancel}' in context.user_data[LIST_TEAM_FAV]:
                    context.user_data[LIST_TEAM_FAV].remove(f'CANCEL {e_cancel}')

                send_text = (f"You have add {e_ball} <b>{team_register}</b> {e_ball}"
                             "to your favorite list Team.\n"
                             "\nSo, I will remind you if your team"
                             f"favorite have schedule matches 🗒 🗒 📆\n"
                             "\nI will send your message <b>before 30</b>"
                             " minutes 🕥 due matches of shedule.")
            else:
                # keep track if a user have add a team favorite
                # even the schedule has expired
                context.user_data[LIST_TEAM_FAV].append(team_register)
                send_text = ("<b>ALL</b> of your team schedule has <b>expired</b>\n"
                             "\nSo, I will remind you again next session ❗️ ❗️\n"
                             "If you want to chose other team\n"
                             f" {e_command} /setfavorite")
        else:
            send_text = (f"Sorry we have problem {e_sad}")

        update.callback_query.edit_message_text(text=send_text)
        logger.info("JOb_queue and insert \n{} team favorite and")
        return END

    def login_end(self, update: Update, context: CallbackContext):
        """The main for this func for manage cancel"""
        
        user_name = update.effective_user.username
        text = (f"Didn't you press inline button {e_qa} {e_qa} \nThen,"
                " you have been <b>END CONVERSATION</b> ❗️ ❗️\n"
                "If you want to stil request, send command again.\n"
                f" {e_command} /setfavorite")
        update.message.reply_text(text=text)

        logging.info('Fallback login: %s', user_name)
        return END

    def login_inline(self, update: Update, context: CallbackContext):
        """The main for this func for manage cancel by inline buttom"""
        # Logging
        user_name = update.effective_user.username
        logging.info('Login_inline_end: %s', user_name)

        text = (f"You have {e_cancel} <b>END CONVERSATION</b> ❗️ ❗ \n"
                "So, I will not add your team favorite in your list 📳 🗒 \n"
                f" {e_command} /setfavorite")
        update.callback_query.edit_message_text(text=text)
        return END

    def logs(self, update, context):
        """Log Errors caused by Updates."""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.error)
        logger.error('Update "%s" caused error "%s"', update, context.error)

    def __process_handler_login(self):

        conv_login = ConversationHandler(
            entry_points=[CommandHandler('setfavorite', self.setmyteam, pass_job_queue=True)
                          ],
            states={
                CHECK: [MessageHandler(Filters.text & ~ Filters.command, self.check_in_db)
                        ],
                VERIFICATION: [CallbackQueryHandler(self.verification_spam,
                                                    pattern='^' + str(YES) + '$',
                                                    pass_job_queue=True),
                               CallbackQueryHandler(self.login_inline,
                                                     pattern='^' + str(CANCEL_FAV) + '$')
                         ],
                REMIND: [CallbackQueryHandler(self.insert_to_remind, pass_job_queue=True,
                                              pattern='^' + str(VERI) + '$'),
                          ],
            },
            fallbacks=[CallbackQueryHandler(self.login_inline, pattern='^' + str(CANCEL_FAV) + '$'),
                       CommandHandler('cancel', self.login_inline, Filters.command),
                       MessageHandler(Filters.all & ~ Filters.command, self.login_end)],
            allow_reentry=True,
            persistent=True,
            name='Control_SetFavorite'
            )
        self.dispatcher.add_handler(conv_login)