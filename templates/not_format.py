from utills.constants_cham import emoji_all

e_command = emoji_all['command']
e_cancel = emoji_all['cancel']
e_location = emoji_all['location']
e_hand = emoji_all['hello']
e_ngece = emoji_all['ngece']
e_ball = emoji_all['ball']
e_phone = emoji_all['contact']
old_zone = emoji_all['timezone']
e_correct = emoji_all['correct']

class TextChat:
    """The main responsibility of this class is text of the view component.

    List command:
    
    /start
    /help
    /seeteam : TO see the schedule of a team
    /setfavorite : To set favorite team of a user
    /listme : To see list of team favorite a user
    /changefav : To change team favorite of a user
    /changeme : To change data of user, e.g. location or number telephone
    /deletme : To delete all data of a user
    /feedbackme : To send a feedback to the developer of bot    
    """

    text_help = ("FEATURE <b>SIGNUP</b>.\n"
                 "<b>List Command.</b>\n"
                 "- /setfavorite <b>arsenal</b> = "
                 "Add schedule team arsenal/your favorite team.\n"
                 "- /listme = To see list of you favorite team.\n"
                 "- /seeteam <b>Arsenal</b> = To see schedule for Arsenal or arsenal.\n"
                 "\nIf you haven't <b>Signup</b> yet, "
                 "We will not allow you to use a command above..!!!\n"
                 "- /start = To <b>start converstation</b>.\n"
                 "- /help = See a <b>command</b>.\n"
                 "- /feedbackme = Send feedback to developer")

    main_menu_text = ("Hi, I can <b>remind you</b> the schedule of matches in the <b>UEFA CHAMPION League..!!</b>.\n"
                      "I only provide the matches schedule <b>Today</b> "
                      "if you haven't <b>Sign Up</b> yet.\n"
                      "I will remind you the schedule matches of your favorite team football.\n"
                      "<b>To SIGNUP,</b> tap the inline button SIGNUP!!\n"
                      "\n<b>SIGNUP, for more feature :</b>\n"
                      "\n---- <b>Feature</b> ---\n"
                      "- /seeteam : To see the schedule of <b>a team</b>.\n"
                      "- /setfavorite : Set your favorite team\n"
                      "- /start : start converstation\n"
                      "- /help :To see a command and more feature.\n"
                      "- /cancel :To exit")

    text_signup_success = ("🎉 🎉 🌹 ✔️ <b>Conguralation you have Signup</b> ✔️ 🌹 🎉 🎉\n"
                           "This is command for more feature.\n"
                           f"\n{e_command} /setfavorite arsenal: "
                           "Add schedule for team arsenal or your favorite team\n"
                           f"\n{e_command} /listme : To see your list team.\n"
                           f"\n{e_command} /seeteam  <b>Arsenal</b> : List schedule for Arsenal or arsenal.\n"
                           "\n\n<b>For more information send command below</b>\n"
                           f"\n{e_command} /start again to see feature\n"
                           f"\n{e_command} /help")
    
    text_has_signup = ("🔐 🤖 🐇 <b>YOU HAVE SIGNUP</b> 🐇 🤖 🔐\n"
                       f"\n{e_command} /setfavorite <b>arsenal</b> = "
                       "Add schedule team arsenal/your favorite team.\n\n"
                       f"\n{e_command} /listme = To see list of you favorite team.\n"
                       f"\n{e_command} /seeteam <b>Arsenal</b> = To see schedule for Arsenal or arsenal.\n"
                       "\n"
                       f"\n{e_command} /start = To see <b>start converstation</b>.\n"
                       f"\n{e_command} /help = To see <b>command</b>.\n"
                       f"\n{e_command} /feedbackme = Send feedback to developer 💻 🤖 ")