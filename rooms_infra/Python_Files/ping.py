import sqlite3
import datetime
from Utils import *

db = '__HOME__/team079/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "Tichu"}


def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        c.execute("UPDATE users SET last_ping = " + str(datetime.datetime.now()) + " WHERE username =\"" + username+"\"")

        # Check if they need to be kicked out of a room

        #Check if anyone else needs to be kicked (because they haven't pinged in 10 seconds)
        need_to_leave = check_online()

        result = c.execute("SELECT * FROM users WHERE username=(?,)", (username,))

        conn.commit()  # commit commands
        conn.close()  # close connection to database

        if username in need_to_leave or result[0][1] == -1 or result[0][2] == -1:
            return "0"
        else:
            #this user doesn't need to leave, but some others do... they will find out when they ping.
            return "1"
