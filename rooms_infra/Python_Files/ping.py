import sqlite3
import datetime

import importlib.util
spec = importlib.util.spec_from_file_location("utils", "var/jail/home/team079/team079/rooms_infra/utils/helpers.py")
Utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Utils)
#
# var/jail/home/username
#
# f
# import sys
# sys.path.insert(0, 'var/jail/home/team079/team079/rooms_infra/utils/')
# from utils import helpers

db = '__HOME__/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "Tichu"}


# Returns:
#           1 = everything ok
#           -1 = leave room (go back to main screen)
#
#

def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        result = c.execute("SELECT * FROM users WHERE username=(?,)", (username,))

        if len(result) == 0:
            conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
            c = conn.cursor()  # move cursor into database (allows us to execute commands)
            c.execute('''INSERT into users VALUES (?,?,?,?);''', (username, -1, -1, datetime.datetime.now()))
            conn.commit()  # commit commands
            conn.close()  # close connection to database

        c.execute("UPDATE users SET last_ping = " + str(datetime.datetime.now()) + " WHERE username =\"" + username+"\"")

        # Check if they need to be kicked out of a room

        #Check if anyone else needs to be kicked (because they haven't pinged in 10 seconds)
        need_to_leave = helpers.check_online()

        for leave_user in need_to_leave:
            helpers.gone_offline(leave_user)

        result = c.execute("SELECT * FROM users WHERE username=(?,)", (username,))

        conn.commit()  # commit commands
        conn.close()  # close connection to database

        room_id = result[0][1]

        if room_id == -1:
            return "-1" # = leave room (go back to main screen)
        else:
            #this user doesn't need to leave, but some others might... they will find out when they ping.
            return "1" # = everything ok
