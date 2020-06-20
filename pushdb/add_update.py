import os
import logging
from pushdb.models import (Session, TeamSchedule,
                           UserData)
# from pushdb.db_updater import
from utills.constants_cham import (DATA_LATITUDE, DATA_LONGITUDE,USER_ID,
                                   USER_SUCCESS_SIGNUP, CHAT_ID, TZINFO,
                                   DATA_CONTACT, NEW_CONTACT)
# sqlalchemy
import pytz
import csv
from datetime import datetime
from utills.ucallendar import change_timezone_of_datetime_object
from sqlalchemy import exc
# job for schedule favorite user
from controller.jobs_main import job_from_login
# LOGGING
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

def add_to_db_user(signup):
    session = Session()
    session.add(signup)
    session.commit()

def add_signup_to_db(context):
    """The main responsibility of this handler is for the button insert data 
    a user to the database.
    Controller: `main_menu` in `controller/control_main.py`
    """
    logger.info(f"Sqlaclhemy Signup data User: {context.user_data['username']}")
    try:
        add_signup = UserData(username=context.user_data['username'],
                              user_id=context.user_data[USER_ID],
                              chat_id=context.user_data[CHAT_ID],
                              name_contact=context.user_data['name_contact'],
                              contact=context.user_data[DATA_CONTACT],
                              latitude=context.user_data[DATA_LATITUDE],
                              longitude=context.user_data[DATA_LONGITUDE],
                              tzinfo=context.user_data[TZINFO],
                              signup_status=context.user_data[USER_SUCCESS_SIGNUP],
                              job_context=True
                              )
        add_to_db_user(signup=add_signup)
        return True
    except KeyError:
        logger.exception('Job context keys not properly initialized.')
        return False
    except Exception:
        logger.exception("Error saving reminder to db.")
        return False

def update_send_to_db(context):
    """This method for update data user in the database (Sqlachemy)
    Controller: controller/control_update.py
    Difference with add_signup_to_db (control_main.py) is either DAT_CONTACT and NEW_CONTACT
    """
    logger.info(f"Sqlaclhemy Update data User: {context.user_data['username']}")
    
    session = Session()
    old_contact = context.user_data[DATA_CONTACT]
    
    dict_update_data = {
        UserData.username: context.user_data['username'],
        UserData.user_id: context.user_data[USER_ID],
        UserData.chat_id: context.user_data[CHAT_ID],
        UserData.name_contact: context.user_data['name_contact'],
        UserData.contact: context.user_data[NEW_CONTACT],
        UserData.latitude: context.user_data[DATA_LATITUDE],
        UserData.longitude: context.user_data[DATA_LONGITUDE],
        UserData.tzinfo: context.user_data[TZINFO],
        }
    try:
        logger.info(f"Sqlaclhemy Update commit")
        query_user = session.query(UserData)
        query_user.filter_by(contact=f'{old_contact}').update(dict_update_data)
        session.commit()
    except Exception:
        logger.info(f"Sqlaclhemy Update commit in Exception")
        session.rollback()
        session.commit()

    return True

def add_to_fav(favorite, chat_id):
    """INSERT INTO Team_favorite many to many"""
    session = Session()
    # find id UserData
    iam = session.query(UserData).filter_by(chat_id=chat_id).first()
    try:
        wenger = session.query(TeamSchedule).filter_by(home_team=f'{favorite}').all()
        for i in wenger:
            iam.champion_league.append(i)
            session.add(iam)
    except exc.SQLAlchemyError:
        session.rollback()
        return False
    finally:
        for r in iam.champion_league:
            result = r.home_team
        if favorite == result:
            session.commit()
            return True
        else:
            return False

def load_csv_sqlalchemy():
    """The main responsibility of this module is for insert data 
    the schedule of league to database when the bot starts.
    datetime str(strptime) must localize (pytz.timezone)
    Then can convert to other timezone with(astimezone)
    File csv (schedule of league) should delimetry by comma
    Column date_time = 2019-09-17 23:55:00 or '%Y-%m-%d %H:%M:%S'
    Column location/stadion: string
    Column home_team: string
    Column away_team: string
    Coulmn group_team: string
    Column result : string
    The timezone in champions-league-2019-SEAsiaStandardTime2.csv file default is asia/jakarta
    """
    try:
        session = Session()
        with open('champions-league-2019-SEAsiaStandardTime2.csv') as data_csv:
            dt_csv = csv.reader(data_csv)
            for row in dt_csv:

                # No error
                # Change the datetime csv file
                # date_date = datetime.strptime(str(row[1]), '%Y-%m-%d %H:%M:%S')
                # conv_date = change_timezone_of_datetime_object(date_date, 'Asia/Jakarta')

                # # Error
                # # date_time = datetime.strptime(str(row[2]), '%H:%M')
                # # conv_time = change_timezone_of_datetime_object(date_time, 'Asia/Jakarta')

                # # test local WIB to Asia/Makassar
                # t_makassar = conv_date.astimezone(pytz.timezone('Asia/Makassar'))
                # td_makassar = t_makassar.strftime('%H:%M')

                # See TeamSchedule is table of Main table
                format_cvs_datetime = '%Y-%m-%d %H:%M:%S'
                dict_datetime = datetime.strptime(str(row[1]),
                                                  format_cvs_datetime)
                record = TeamSchedule(
                    **{'round_number': row[0],
                       'date_time': dict_datetime,
                        # 'date_time': conv_date.strftime('%H:%M'),
                        # date_time': td_makassar,
                        # 'date_time': conv_time.strftime('%H:%M'), ERROR
                       'location': row[2],
                       'home_team': row[3],
                       'away_team': row[4],
                       'group_team': row[5],
                       'result_final': row[6]
                       })
                session.add(record)
                print('\n')
                print(str(row[1]))
                print(str(row[0]))
            try:
                session.commit()
                return True
            except exc.SQLAlchemyError as e:
                # fixing this
                logger.info('Error File not found %s', e)
                session.rollback()
                session.commit()
                return True
        return True
    except (EnvironmentError, IOError, OSError):
        logger.info('Error File not found')
        return False
