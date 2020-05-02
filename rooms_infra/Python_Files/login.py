import sqlite3
#import sys
#sys.path.insert(0, "~/team079/rooms_infra/Python_Files/helpers.py")
#from helpers import *
import datetime

db = '__HOME__/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "PushUps"}

def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)
        c.execute('''INSERT into users VALUES (?,?,?,?);''', (username, -1, -1, datetime.datetime.now()))
        conn.commit()  # commit commands
        conn.close()  # close connection to database

        return "Hello user "+username+", you are online!"
