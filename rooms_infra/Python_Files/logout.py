import sqlite3
import datetime
import random
import sys
sys.path.append('__HOME__/team079/rooms_infra/Python_Files')
import helpers

db = '__HOME__/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "PushUps"}

def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        result = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchall()

        if len(result) > 0:
            helpers.gone_offline(username, result[1], result[2], conn, c)


        return "1"