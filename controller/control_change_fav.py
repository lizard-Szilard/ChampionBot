import copy
import logging
from telegram.ext import (ConversationHandler, CommandHandler,
                          MessageHandler, Filters, CallbackContext,
                          CallbackQueryHandler)
from telegram import Update, ChatAction
# Keyboard Costume
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
# Restrict Permission
from utills.utils import restricted_non_signup, send_action
from utills.permission import restricted_chat
# List Team Fav User nd Emoji
from utills.constants_cham import LIST_TEAM_FAV, emoji_all, END
# Sqlalchemy And List Team
from utills.utils import remove_duplicate_list

# remove_fav_team
from pushdb.models import Session, UserData, TeamSchedule
from jinja2 import (Environment, FileSystemLoader)

# Emoji
bolla = emoji_all['ball']
command_e = emoji_all['command']
ask_e = emoji_all['QA']
cancel_e = emoji_all['cancel']

# Definition state
CHANGE_FAV_ONE = 53290141
REMOVE_TEAM = 46425713

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

import time
from utills.dict_in_memory import DATA_JOB

@restricted_chat 
@restricted_non_signup
@send_action(ChatAction.TYPING)
def change_fav(update: Update, context: CallbackContext):
    """The main responsibility of this module is for '/changefav' command.
    The /changefav command is for change team favorite of a user.
    """
    logger.info("/changefav command")
    user = update.effective_user

    if not context.user_data.get(LIST_TEAM_FAV):
        text_exit = ("Well, You haven't <b>Team Favorite</b>\n"
                     f" {command_e} /setfavorite for add a team to your list")
        user.send_message(text_exit)
        logger.info("/changefav don't have Team Favorite")
        return END
    elif len(context.user_data[LIST_TEAM_FAV]) == 0:
        text_exit = ("Well, You haven't <b>Team Favorite</b>\n"
                     f" {command_e} /setfavorite for add a team to your list")
        user.send_message(text_exit)
        logger.info("/changefav don't have Team Favorite")
        return END
    else:
        list_duplicate = copy.deepcopy(context.user_data[LIST_TEAM_FAV])
        list_team = remove_duplicate_list(list_duplicate, addional_data=f'CANCEL {cancel_e}')
        logger.info('Change Favorite Team,\nSleep 2 times change_fav')

        time.sleep(2)
        
        # Text
        button_list = [[KeyboardButton(s)] for s in list_team]
        keyboard_costume = ReplyKeyboardMarkup(button_list, selective=True)
        text = f"{bolla} Your <b>Team Favorite</b> {bolla}"
        user.send_message(text=text, reply_markup=keyboard_costume)

        logger.info(f"Remove Team Favorite\nUser: {user.username}\n"
                    f"Team favorite: {list_team}")
        return CHANGE_FAV_ONE

def remove_or_no(update: Update, context: CallbackContext):
    user = update.effective_user
    request_remove = update.message.text
    logger.info(f"User: {user.username} in remove_favteam module: {request_remove}")

    list_team = context.user_data[LIST_TEAM_FAV]
    if request_remove not in list_team:
        text = ("I think you are not using <b>Keyboard Costumes</b>. LoL")
        remove_keyboard = ReplyKeyboardRemove()
        user.send_message(text, reply_markup=remove_keyboard)
        return END
    else:
        # Get Name Team
        context.user_data['Remove_fav_team_changefav'] = request_remove
        sure_button = KeyboardButton(f"SURE {ask_e}")
        cancel_button = KeyboardButton(f"CANCEL {cancel_e}")
        text = "Oke, I ask once agian"
        keyboard_costume = [[sure_button], [cancel_button]]
        user.send_message(text, reply_markup=ReplyKeyboardMarkup(keyboard_costume))
        return REMOVE_TEAM

def remove_fav_team(update: Update, context: CallbackContext):
    """Delete team favorite a user in Sqlalchemy and in DATA_JOB"""
    user = update.effective_user
    chat = update.effective_chat
    job_data = DATA_JOB[chat.id]
    team_remove = context.user_data['Remove_fav_team_changefav']
    
    # Remove Job and List club at context.user_data[LIST_TEAM_FAV]
    logger.info(f"Remove Job and List Team: {team_remove}")
    if team_remove in context.user_data[LIST_TEAM_FAV]:
        list_team = context.user_data[LIST_TEAM_FAV]
        list_team.remove(team_remove)
        if f"CANCEL {cancel_e}" in list_team:
            list_team.remove(f"CANCEL {cancel_e}")
            context.user_data[LIST_TEAM_FAV] = list_team
        # Remov by job
        print(f"job_data {job_data}")
        if job_data.get(team_remove) and job_data[team_remove] != 0:
            print(job_data[team_remove])
            for job in job_data[team_remove]:
                job.schedule_removal()
            del job_data[team_remove]
    else:
        text = "Sorry you are wrong input"
        user.send_message(text, reply_markup=ReplyKeyboardRemove())
        return END
            
    logger.info("Process.. remove in db SQLALCHEMY")
    session = Session()
    # Query UserData
    q_user = session.query(UserData)
    join_user = q_user.join(TeamSchedule.user).filter_by(chat_id=chat.id).first()
    query_team = session.query(TeamSchedule).filter_by(home_team=str(team_remove)).all()
    total_schedule = [join_user.champion_league.remove(team_user) for team_user in query_team]
    session.commit()
    session.close_all()
    
    ZERO = 0
    if len(total_schedule) is not ZERO:
        logger.info(f"Total: {len(total_schedule)} shedule team: {team_remove}")
        text = (f"You have remove <b>{team_remove}</b> which has "
                f"<b>{len(total_schedule)}</b> schedule total")
    else:
        text = (f"Sorry we have problem")
        return END
    user.send_message(text, reply_markup=ReplyKeyboardRemove())
    return END

def cancel_fav(update: Update, context: CallbackContext):
    user = update.effective_user
    logger.info(f"User: {user.username} CANCEL /changefav")

    text = ("You have <b>CANCEL</b> to REMOVE your list team favorite or\n"
            f" from {command_e} /changefav")
    user.send_message(text, reply_markup=ReplyKeyboardRemove())
    return END

def logs_change_fav(update, context):
    """Log Errors caused by Updates."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.error)
    logger.error('Update "%s" caused error "%s"', update, context.error)

conv_change_fav = ConversationHandler(
    entry_points=[CommandHandler('changefav', change_fav)
                  ],
    states={
        CHANGE_FAV_ONE: [MessageHandler(Filters.text & ~ Filters.regex(f'^(CANCEL {cancel_e})$'),
                                        remove_or_no)
                         ],
        REMOVE_TEAM: [MessageHandler(Filters.regex(f'^(SURE {ask_e})$'), remove_fav_team)
                      ]
        },
    fallbacks=[MessageHandler(Filters.regex(f"^(CANCEL {cancel_e})$"), cancel_fav),
               CommandHandler('cancel', cancel_fav)
               ],
    allow_reentry=True,
    persistent=True,
    name='conv_change_fav'
    )