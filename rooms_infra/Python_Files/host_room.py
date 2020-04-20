import sqlite3
import datetime
from Utils import *

db = '__HOME__/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "Tichu"}


def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])
        game_id = int(args['game_id']) #0 or 1 or 2 etc

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        room_id = int(c.execute('''SELECT MAX(room_id) FROM rooms''')[0]) + 1
        c.execute('''INSERT into rooms VALUES (?,?,?,?,?);''', (room_id, username, 1, game_id, datetime.datetime.now()))
        c.execute('''INSERT into games VALUES (?,?,?);''', (game_id, room_id, 1, datetime.datetime.now()))

        conn.commit()  # commit commands
        conn.close()  # close connection to database

        message = "Welcome to room " + str(room_id) + ".\n"
        message += "You are playing game " + GAME_ID_TO_NAME[str(game_id)]+"."

        return message
