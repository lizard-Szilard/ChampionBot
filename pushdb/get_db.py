import sys
import logging
from datetime import date, timedelta

import psycopg2
from psycopg2 import (DatabaseError, DataError, InterfaceError,
                      OperationalError, ProgrammingError, extras,
                      OperationalError)
from pushdb.persistencedb import PSQLdbconn as Database

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR)

logger = logging.getLogger(__name__)


class GetDatabase:
    """GetDatabase use psycopg2 driver
    This class for get database
    Example:
        Get schedule for today, tommorow, yesterday
    """
    def __init__(self, db_name):
        self.db_connect = db_name

    def get_from_date(self, datetime_db, zone_time='asia/jakarta'):
        """
        Using psycopg2
        Get database for specifict date or time
        Params specifict_colum: date or time
        select date_time at time zone 'asia/makassar' from champion_league where;
        select date_time at time zone 'asia/jakarta' from champion_league_try where date_time=current_date;
        datetime format: 1999-12-30 or  Python format '%Y-%m-%d'
        Return: fetchall()
        """
        dbquery = (f"SELECT *, date_time AT TIME ZONE '{zone_time}' FROM "
                   "champion_league WHERE "
                   f"date_time::text LIKE '{datetime_db} %';")
        try:
            with Database(self.db_connect) as db:
                db.query(dbquery)
                finish = db.fetchall()

                if 0 != len(finish):
                    logger.info('Database `get_from_date` success')
                    return finish
                else:
                    return
        except DatabaseError as e:
            logger.error(f'DatabaseError:', e)
            sys.exit(1)
        except OperationalError as e:
            logger.error(f'Unable Connection:\n{e}')
            sys.exit(1)

    def select_team(self, team_club):
        """select column base on home_team use psycopg2
        param: must have value"""

        string_user = str(team_club.lower())
        team_front = string_user[0:3]
        team_back = string_user[-3:len(string_user)]

        """postgresql regex

        '^' begin of query,
        '$' = end of query,
        '~*' = matches case insentisitive"""

        dbquery = ("SELECT * FROM champion_league WHERE "
                   "home_team ~*'^{}' AND "
                   "home_team ~*'{}$';".format(team_front, team_back))

        with Database(self.db_connect) as db:
            try:
                db.query(dbquery)
                finish = db.fetchall()
            except psycopg2.Error as e:
                logger.error(e)
                sys.exit(1)
            except DatabaseError as e:
                logger.error(f'databaseerror:', e)
                return
            except OperationalError as e:
                logger.error(f'unable connection:\n{e}')
                sys.exit(1)
        # Logger
        logger.info('Module select_team. Team: {}'.format(string_user))

        return finish

    def select_seeteam(self, team_club, zone):
        """This module psycopg2 for the /seeteam command
        Args:
            team_club (string): The name a team should more 3 character
            zone (string): Timezone user
        Return : if a team not exist in the database return None
        postgresql regex
        '^' begin of query,
        '$' = end of query,
        '~*' = matches case insentisitive
        """
        string_user = str(team_club.lower())
        team_front = string_user[0:3]
        team_back = string_user[-3:int(len(string_user))]
        print(string_user, team_front, team_back, zone)

        dbquery = (f"SELECT *, date_time AT TIME ZONE '{zone}' "
                   f"FROM champion_league WHERE home_team ~*'^{team_front}' AND "
                   f"home_team ~*'{team_back}$';")
        
        with Database(self.db_connect) as db:
            try:
                db.query(dbquery)
                finish = db.fetchall()
                if len(finish) != 0:
                    logger.info(f'Model: selec_seeteam. Team: {string_user}, Timezone: {zone}')
                    return finish
                else:
                    logger.info(f'Model: selec_seeteam retrun: None')
                    return
            except psycopg2.Error as e:
                logger.info(e)
                sys.exit(1)
            except DatabaseError as e:
                logger.info(f'databaseerror:', e)
            except OperationalError as e:
                logger.info(f'unable connection:\n{e}')
                sys.exit(1)