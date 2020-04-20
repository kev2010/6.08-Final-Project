import sqlite3
# from Utils.py import *
import datetime

db = '__HOME__/team079/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "Tichu"}

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


