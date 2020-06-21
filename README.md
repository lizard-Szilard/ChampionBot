# ChampionBot

This is repository code for **unofficial Champion UEFA league telegram bot**.

### **NOTICE:** 
1. The documentation of repository code needs improvent.
2. This bot used the [pickle module python](https://docs.python.org/3/library/pickle.html) for store some information about the current user and/or chat for later use, it's not good approachment to use the pickle module python for store a information about the bot becuase the pickle module python is not secure, [you can change that approachment](https://github.com/lizard-Szilard/ChampionBot#guide-modify-the-schedule-of-league)
3. We tested this bot only on Debian 10 (Buster) distro based on the GNU/Linux system.

## Description

This is a telegram bot which can reminder the user of the bot about the schedule of Champion UEFA league. It's only compatible with Python version 3.5+ and use a [Telegram wrapper API bot (python-telegram-bot)](https://github.com/python-telegram-bot/python-telegram-bot). 

This bot is based on **[MVC model](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)**. Also the bot can manage other schedules football leagues but requires changes on the **model database component** and the **view component** (needs documentation). 
The schedule of Champion UEFA league from [fixturedownload](https://fixturedownload.com/)

## Installation

* **NOTE:** This tutorial installation on **Debian 10 (Buster) GNU/Linux system**

The file csv is the schedule Champion UEFA league that must in the root directory of code to be included to the database. This behavior can be changed, see in the `ChampionBot/main.py` file on line 107.

#### Clone the repository code
```bash
$ git clone https://github.com/lizard-Szilard/ChampionBot.git
$ cd ChampionBot/
$ pip install -r requirements.txt
```

#### Setting up the bot.
* **Install postgresql**, see [wiki Debian postgresql](https://wiki.debian.org/PostgreSql)

First of all, you have to create a new Telegram bot using [BotFather](https://telegram.me/botfather) and get the bot token, then you should edit a `config.py` file and to set up your bot and the database.

```python3
# Token bot
TOKEN = 1234
# Config the engine Sqlalchemy
SQLALCHEMY_URI = 'postgres+psycopg2://postgres:postgres@localhost/postgres'
# URI Postgresql
DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/postgres'
```

### Run the bot
```bash
$ sudo systemctl start postgresql.service
$ cd ChampionBot/
$ python main.py
```
After run the bot, you can test the bot by send a command message **/start** or **/help** to the bot.

## How does the bot work?
- Command List
    * **/start** : Start conversation
    * **/help** : Get help
    * **/football** : Sign up and to see the schedule of today
    * **/setfavorite** : Set favorite a team (A user has max 5 team favorite).
    * **/listme** : To see list favorite a user
    * **/seeteam** : To see the schedule of a team match
    * **/changefav** : To delete a team from list favorite
    * **/changme** : To changes data of a user
    * **/feedbackme** : To send a feedback for the developer
    * **/deleteme** : To delete all data of a user

## Storing data
#### What should I know?
Actually use the pickle module it is enough, but I give you an option.

1. [PTB Making your bot persistent](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Making-your-bot-persistent)
2. [PTB Documentation](https://python-telegram-bot.readthedocs.io/en/latest/telegram.ext.basepersistence.html)

Good approachment is using the **PTB** [telegram.ext.basepersistence](https://python-telegram-bot.readthedocs.io/en/latest/telegram.ext.basepersistence.html) module.
After write code for **BasePersistance** you can put that code in the `ChampionBot/pushdb/` directory, it's for the **model component** based on MVC architecture. Then you can change some code in file `ChampionBot/main.py` on line 54-57, see [telegram.ext.Updater](https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.updater.html#telegram.ext.Updater.persistence).

## Guide modify the schedule of league

First of all you needs schedules of league in a CSV file. The CSV should delimetry by comma.
* CSV file of the schedule of league.

```csv
round_number,date_datetime,location,home_team,away_team,group_team,result_match
1,2019-09-17 23:55:00,Stadio San Siro,Internazionale,Slavia Praha,Group F,1 - 1
```
That header will be column table of the database.
Put your CSV in the root of directory. You should remove the header of CSV, That CSV file will inserting to the databse during the bot starts.
A `date_datetime` object should following `2019-09-17 23:55:00` format.

If you modify the column name, you should edit the templates. The Output of templates is directly from postgresql (psycopg2 driver).
#### The rules
- You can modify all of the name of column except list below.
 * Don't change `home_team` column of the database.
 * Don't change `date_datetime` column and format.

# Authors
* Telegram username [Liard Ohama || Szilard](https://t.me/kentaro_ohama)
