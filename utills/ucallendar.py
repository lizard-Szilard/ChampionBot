import logging
import json
from datetime import datetime
import pytz
from pytz import timezone, utc
from pytz.exceptions import UnknownTimeZoneError
from timezonefinder import TimezoneFinder

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class TimeUtils:
    """
    Class Calltime:
        This Class for convert timezone
        Default Timezone construct class:
        Asia/Jakarta (WIB): GMT +07:00 	+25200 (0 hour)
        Asia/Jakarta = latit:-8.088403 longi:111.849324

        provide convert NAIVE to AWARE UTC
        Asia/Jakarta (WIB): GMT +07:00 	+25200 (0 hour)
        Asia/Jakarta = latit: -8.088403, longi:111.849324
        Asia/Makassar (WITA): GMT +08:00 +28800  (1 hours)
        Asia/Jayapura (WIT): GMT +09:00 +32400 (2 hours)

        Parameters latit: equivalent latitude Asia/Jakarta
        Parameters longi: equivalent longitude Asia/Jakarta
        Parameters unix_epoch=0(int): update.message.date
    """

    def __init__(self, latit=-8.088403, longi=111.849324, unix_epoch=0):
        self.latit = latit
        self.longi = longi
        self.unix_epoch = unix_epoch

    def time_aware(self):
        """
        Convert datetime unix_epoch(update.message.date) to specifict UTC
        timezone local, default Asia/Jakarta in parameters construct

        Return: json_datetime = {'date': aware_date,
                                'time': aware_time,
                                'zone': t_zone}
        format date: 2020-07-30 '%Y-%m-%d'
        format time: 24:50:00 '%H:%M:%S'
        format zone: 'continent/city' (str)
        """
        tf = TimezoneFinder()
        tzone_user = tf.timezone_at(lng=self.longi, lat=self.latit)

        try:
            t_utc = utc.localize(self.unix_epoch)
            t_to_user = t_utc.astimezone(timezone(tzone_user))
            fmt_date = '%Y-%m-%d'
            fmt_time = '%H:%M:%S'
            fmt_zone = '%z:%Z'
            aware_time = datetime.strftime(t_to_user, fmt_time)
            aware_date = datetime.strftime(t_to_user, fmt_date)
            # t_zone = datetime.strftime(t_to_user, fmt_zone)

            json_datetime = {
                'date': aware_date,
                'time': aware_time,
                'tzinfo': tzone_user
            }
            finish = json.dumps(json_datetime)
            
            logger.info(f'Today in datetime USER: {t_to_user}')
        except UnknownTimeZoneError as e:
            logger.info("Unknow Timezone: %s", e)
        return finish

def change_timezone_of_datetime_object(date_time_object, new_timezone_name):
    """Return the *date_time_object* with it's timezone changed to *new_timezone_name*
    :param date_time_object: The datetime object whose timezone is to be changed
    :type date_time_object: datetime
    :param new_timezone_name: The name of the timezone to which the *date_time_object* is to be changed to
    :type new_timezone_name: str
    :rtype: datetime
    """
    # Create a pytz.timezone object for the new_timezone
    new_timezone_object = pytz.timezone(new_timezone_name)
    # Update the timezone of the datetime object
    date_time_ob = date_time_object.astimezone(new_timezone_object)
    # Return the converted datetime object
    return date_time_ob