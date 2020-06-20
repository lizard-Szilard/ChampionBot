from functools import wraps
from telegram.utils.helpers import mention_html
# Emoji
from utills.constants_cham import emoji_all
from telegram import Update
from telegram.ext import CallbackContext

e_command = emoji_all['command']
e_cancel = emoji_all['cancel']
e_location = emoji_all['location']
e_hand = emoji_all['hello']
e_ngece = emoji_all['ngece']
e_ball = emoji_all['ball']
e_phone = emoji_all['contact']
old_zone = emoji_all['timezone']
e_correct = emoji_all['correct']

# This snippet code from
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#restrict-access-to-a-handler-decorator

# LIST_OF_ADMINS = [12345678, 87654321]
# 
# def restricted(func):
#     @wraps(func)
#     def wrapped(update, context, *args, **kwargs):
#         user_id = update.effective_user.id
#         if user_id not in LIST_OF_ADMINS:
#             print("Unauthorized access denied for {}.".format(user_id))
#             return
#         return func(update, context, *args, **kwargs)
#     return wrapped


# This permission only for handler non Class because whe can't
# add return end in this wrapper and wrapper for class need self argument

def restricted_chat(func):
    """restrict chat for the handler fucntion"""
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        print('wrape for permission_chat')
        type_chat = update.effective_chat.type

        if type_chat in LIST_OF_TYPE_CHAT:
            chat_id = update.effective_chat.id
            bot_mention = context.bot.name
            user_mention = mention_html(update.effective_user.id,
                                        update.effective_user.full_name)
            text_group = (f"I'm not allow to using this feature in <b>public chat</b> {e_ngece}\n"
                          f"\n<b>PM {bot_mention}</b>\n"
                          "\nI have send your message.\n"
                          "if you want to using this"
                          f" feature\n {user_mention}"
                          )
            context.bot.send_message(chat_id=chat_id,
                                     text=text_group)

            print("Unauthorized access denied for {}.".format(type_chat))
        return func(update, context, *args, **kwargs)
    return wrapped


LIST_OF_TYPE_CHAT = ['group', 'channel', 'supergroup']
def restricted_chat_class(func):
    """The main responsibility is allow user only in private chat.
    This decorator for a handler class.
    """
    # This not related with erro
    # print('restricted_chat')
    @wraps(func)
    def wrapped(self, update: Update, context: CallbackContext, *args, **kwargs):
        print('wrape for permission_chat')
        type_chat = update.effective_chat.type
        
        if type_chat in LIST_OF_TYPE_CHAT:
            chat_id = update.effective_chat.id
            bot_mention = context.bot.name
            user_mention = mention_html(update.effective_user.id,
                                        update.effective_user.full_name)
            text_group = (f"I'm not allow to using this feature in <b>public chat</b> {e_ngece}\n"
                          f"\n<b>PM {bot_mention}</b>\n"
                          "\nI have send your message.\n"
                          "if you want to using this"
                          f" feature\n {user_mention}"
                          )
            context.bot.send_message(chat_id=chat_id,
                                     text=text_group)

            print("Unauthorized access denied for {}.".format(type_chat))
        return func(self, update, context, *args, **kwargs)
    return wrapped