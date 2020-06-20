from telegram.ext import ConversationHandler
from pushdb.models import Session, UserData
from telegram.ext import BaseFilter

# For persistance data 

# Control_main -- Key user_data for remove specifict feature
# Constans variable Idenfier a user Signup or Non
# This should delete when user non signup
USER_SUCCESS_SIGNUP = 'USER_SUCCESS_SIGNUP'
# Keep track list team favorite a user
LIST_TEAM_FAV = 'LIST_TEAM_FAV'

# Control main -- Top State definitions
FIRST, SIGNUP_STATE = 5000, 5001
# Signup main -- Second State definitions
(USER_SIGNUP, REMOVAL, STACK_LOCATION, STACK_CONTACT,
 FINISH, DB_SAVE, BACK_FINISH) = 5002, 5003, 5004, 5005, 5006, 5007, 'False'
# Confirmation signup finish
LOCATION_FINISH , INLINE_CONF = 1414, 1415
# Control main InlineKeyboardButton callback_data
TODAY, SIGNUP, EXIT_FOOTBALL = 5008, 5009, 5010
# Signup main Different constants
SIGNUP_TOFINSIH = 6000
# Key user_data for category database Signup and Update data user
# File update_delete.py and control_main.py
(DATA_LATITUDE, DATA_LONGITUDE,
 DATA_CONTACT) = 'latitude', 'longitude', 'contact'
USER_ID, CHAT_ID, TZINFO = 'user_id', 'chat_id', 'TimeZone'
# Be carefull with NEW_CONTACT because for identifier
NEW_CONTACT = 'NEW_CONTACT'

# Control main Shortcut
END = ConversationHandler.END

# Control Login -- State definition Control_login.py (ControlLogin)
CHECK, VERIFICATION, REMIND = 50, 51, 52
# Data Qeury Callback
YES, CANCEL_FAV, AGAIN, VERI = 8989, 9998, 101010, 100100
# user data definition
CLUB = 100110

# Control help/LittleFeature -- State definition Control_help.py
REQUEST_SEE = 501010
# Control FeedBack -- State definition Control_help.py
REQUEST_FEEDBACK = 500000
# Callback data for update_dele/ChangeDataUser
YES_CHANGE_DATA, NO_CHANGE_DATA, CONFIRM_CHANGE_DATA = 'YES_CHANGE_DATA', 'NO_CHANGE_DATA', 'CONFIRM_CHANGE_DATA'

emoji_all = {"command": "🔑", "location": "📍", "contact": "📞", "QA": "❓", "cancel": "🙅",
             "timezone": "⏲", "hello": "🖐", "ngece": "😏", "ball": "⚽️", "correct": "✔",
             "end": "🔚", 'cs': '💻', "party": "🎉", "sad":"😞"}