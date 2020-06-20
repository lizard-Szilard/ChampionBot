import pytz
import logging
from datetime import timedelta, datetime
from pushdb.models import Session, TeamSchedule, UserData
from utills.utils import dict_init_context
from telegram import ParseMode
# A key Job and The shelver contain job
from utills.constants_cham import CLUB
# Dict in-memory
from utills.dict_in_memory import DATA_JOB
from controller.jobs_main import notif_for_job
from utills.utils import remove_duplicate_list
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING)
logger = logging.getLogger(__name__)

def load_job_mian(job_q):
    """The main responsibility of this module is for restroe job.queue after the bot stop"""
    identifier = list()    
    dt_continue = datetime.now()
    try:
        logger.info("Register... Job /setfavorite")
        # get schedule PER-CLUB
        session = Session()
        query_user = session.query(UserData)
        query_join = query_user.join(TeamSchedule.user).filter_by(job_context=True).all()

        for q_user in query_join:
            if q_user.job_context is True:
                team_fav = [row.home_team for row in q_user.champion_league]
                remove_duplicate = remove_duplicate_list(team_fav)
                for team_here in remove_duplicate:
                    identifier.append(team_here)
                    list_job_remove = list()
                    query_team = session.query(TeamSchedule).filter_by(home_team=team_here).all()
                    dt_now = dt_continue.astimezone(pytz.timezone(q_user.tzinfo))
                    for row_team in query_team:
                        dt_zone_team = row_team.date_time.astimezone(pytz.timezone(q_user.tzinfo))
                        # Filter for skipe datetime has expired
                        if dt_zone_team <= dt_now:
                            continue
                        due_job = dt_zone_team - timedelta(minutes=30)
                        # This will assign to job per-team
                        # Get context for job.
                        # result is from db jinja
                        result = dict_init_context(team=row_team,
                                                   user=q_user,
                                                   addional=dt_zone_team)
                        # Register a Job
                        permanent = job_q.run_once(notif_for_job,
                                                   when=due_job,
                                                   context=result)
                        list_job_remove.append(permanent)
                        logger.info("Register JOB of /setfavorite end")
                    # Key is name of team so it's will easy to delete specifict team and
                    # Job is list cointain a job
                    ZERO = 0
                    if len(list_job_remove) is not ZERO:
                        # key_team = str(row_team.home_team)
                        if len(identifier) == 1:
                            print(f'FIRST time DATA_JOB {len(list_job_remove)} {team_here}')
                            key = {team_here: list_job_remove}
                            DATA_JOB[q_user.chat_id] = key
                        else:
                            print(f'SECOND time DATA_JOB {len(list_job_remove)} {team_here}')
                            key = DATA_JOB[q_user.chat_id]
                            key[team_here] = list_job_remove
                            DATA_JOB[q_user.chat_id] = key
                            
                        logger.info(f"Register.. DATA_JOB: {DATA_JOB}")
        session.close_all()
    except (Exception, ValueError) as e:
        logger.warning(f"Job Favorite Error {e}")