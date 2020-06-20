import os
import pytz
import logging
from datetime import timedelta, datetime
from pushdb.models import Session, TeamSchedule, UserData
from utills.utils import dict_init_context
from telegram import ParseMode
# A key Job and The shelver contain job
from utills.constants_cham import CLUB

# Test pickle and shavle
# from utills import (save_shelve, change_update_shelve, load_shelve)
# from utills import (save_pickle, load_pickle)
# Test for Update bot_data
# Enable logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING)
logger = logging.getLogger(__name__)
from utills.dict_in_memory import DATA_JOB
def job_from_login(update, context):
    """
    This module for depencency controller/control_login.py
    TODO: Get datetime from PER-CLUB using join [ ✔️ ]
    TODO: Set up jinja/result/job_q context. must create dict object [ ✔️ ]
    TODO: Find out way to 'cancel' a job has register to 
    the job [ ✔️ ] --> It's possible to purge/canel all job not per-team
    """
    chat_id = update.effective_chat.id
    job_q = context.job_queue
    team = context.chat_data[CLUB]
    list_job_remove = list()
    dt_continue = datetime.now()
    try:
        logger.info("Register... Job /setfavorite")
        # get schedule PER-CLUB
        session = Session()
        query_user = session.query(UserData).join(TeamSchedule.user).\
            filter_by(chat_id=f"{chat_id}").all()

        for row in query_user:
            dt_now = dt_continue.astimezone(pytz.timezone(row.tzinfo))
            for row_team in row.champion_league:
                # Chose favorite user
                if team != row_team.home_team:
                    continue
                dt_zone_team = row_team.date_time.astimezone(pytz.timezone(row.tzinfo))
                zone_user = pytz.timezone(row.tzinfo)
                # Filter for skipe datetime has expired
                if dt_zone_team <= dt_now:
                    continue
                # BUG
                before = dt_zone_team - timedelta(minutes=10)
                register_team = row_team
                due_job = zone_user.normalize(before + timedelta(minutes=10))
                print('register_team')
                # This will assign to job per-team
                # Get context for job.
                # result is from db jinja
                result = dict_init_context(team=register_team, user=row, addional=dt_zone_team)
                # Register a Job
                permanent = job_q.run_once(notif_for_job, when=due_job, context=result)
                # Update Sqlachemy
                row.job_context = True
                list_job_remove.append(permanent)
                logger.info("Register JOB of /setfavorite end")
        # Key is name of team so it's will easy to delete specifict team and
        # Job is list cointain a job
        logger.info(f"JOB_list: {list_job_remove}")
        ZERO = 0
        if len(list_job_remove) is ZERO:
            logger.info(f"Register.. DAT_JOB[key][team] = 0")
            session.close()
        
        logger.info(f"Register.. DAT_JOB[key][team] = True")
        team_key = str(register_team.home_team)
        key = DATA_JOB[chat_id]
        key[team_key] = list_job_remove
        DATA_JOB[chat_id] = key
        print(f"DATA_JOB: {DATA_JOB[chat_id]}")
        session.commit()
        session.close()
        return True
    except (Exception, ValueError) as e:
        logger.warning(f"Job Favorite Error {e}")
        return False

def notif_for_job(context):
    """The main responsibility of this handler is for send message by the job.run_once.
    Controller: `job_from_login` above
    Templates: job_text.txt
    """
    job = context.job
    context.bot.send_message(chat_id=job.context['chat_id'],
                             text=job.context['send_text'])
    logger.info('Send notif JOB_team_fav')