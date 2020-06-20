from config import TOKEN
import sys, logging
from os import environ
# PTB Module
from telegram.ext import (Updater, CommandHandler,
                          PicklePersistence, Job, Defaults)
from telegram import ParseMode
# Module help
from controller.control_help import help_module, start_me
from controller.control_myfav import my_fav
from controller.control_feedback import FeedBackUSer
from controller.control_seeteam import SeeTeam
# Module main feature
from controller.control_main import conversation_main, logs_main
from controller.control_setfavorite import ControlSetFavorite
# Moduler for update/change user data database
from controller.control_update import conv_change_data, logs_update_delete
# Module for control_delete.py
from controller.control_delete import conv_request_delete, logs_delete_request
# Module for change favorite user
from controller.control_change_fav import conv_change_fav, logs_change_fav
# Pickle persistent job
import pickle
from pushdb.persist_pickle import save_jobs, save_jobs_job, load_jobs
from datetime import timedelta

# sqlalchemy
from sqlalchemy import exc
from pushdb.models import Session, TeamSchedule
from pushdb.add_update import load_csv_sqlalchemy
from pushdb.load_job import load_job_mian
from utills.dict_in_memory import DATA_JOB

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

def main():

    default = Defaults(parse_mode=ParseMode.HTML)
    P_pickle = PicklePersistence('Persitance_data.pickle')
    updater = Updater(token=TOKEN,
                      use_context=True,
                      persistence=P_pickle,
                      defaults=default)
    # Load job
    logger.info('Load_job_main DB')
    # Restrore job.queue
    load_job_mian(updater.job_queue)
    dp = updater.dispatcher

    # Control Main
    dp.add_handler(conversation_main)
    dp.add_error_handler(logs_main)

    # Control login
    login_control = ControlSetFavorite(dispatcher=dp)
    dp.add_error_handler(login_control.logs)

    # help module and LittleFeature
    litte_f = SeeTeam(dispatcher=dp)
    dp.add_error_handler(litte_f.logs_seeteam)

    # Module help and Feedback
    feeback_user = FeedBackUSer(dispatcher=dp)
    dp.add_error_handler(feeback_user.logs_feedback)

    # For control_delete.py
    dp.add_handler(conv_request_delete)
    dp.add_error_handler(logs_delete_request)

    # Module update/change data user in database
    dp.add_handler(conv_change_data)
    dp.add_error_handler(logs_update_delete)

    # Module for change favorite user
    dp.add_handler(conv_change_fav)
    dp.add_error_handler(logs_change_fav)

    startku = CommandHandler('start', start_me)
    dp.add_handler(startku)

    fav_user = CommandHandler('listme', my_fav)
    dp.add_handler(fav_user)

    help_command = CommandHandler('help', help_module)
    dp.add_handler(help_command)

    updater.start_polling(poll_interval=1)
    updater.idle()

if __name__ == "__main__":

    try:
        # Insert the schedule of league to the database if the data no exist
        session = Session()
        team_schedule = session.query(TeamSchedule.id).filter_by(id=1).all()
        if 0 == len(team_schedule):
            load_sucess = load_csv_sqlalchemy()
            team_schedule = session.query(TeamSchedule.id).filter_by(id=1).all()
            if load_sucess is True and len(team_schedule) is not 0:
                main()
            else:
                sys.exit(1)
        else:
            main()
    except exc.SQLAlchemyError:
        sys.exit(1)
