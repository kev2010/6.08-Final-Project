import sqlite3
import datetime
import uuid
# from Utils import *

db = '__HOME__/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "PushUps"}


def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])
        game_id = int(args['game_id']) #0 or 1 or 2 etc

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        # room_id = int(c.execute('''SELECT MAX(room_id) FROM rooms''')[0]) + 1
        room_id = str(uuid.uuid4()) # generate room id
        c.execute('''INSERT into rooms VALUES (?,?,?,?,?);''', (room_id, username, 1, game_id, datetime.datetime.now()))
        c.execute('''INSERT into games VALUES (?,?,?,?);''', (game_id, room_id, 1, datetime.datetime.now()))
        c.execute('''UPDATE users SET room_id = ? WHERE username = ?;''', (room_id, username))
        c.execute('''UPDATE users SET game_id = ? WHERE username = ?;''', (game_id, username))
# (game_id int, room_id int, capacity int, start_time timestamp);''')


        conn.commit()  # commit commands

        result = c.execute('''SELECT * FROM rooms''').fetchall()
        conn.close()  # close connection to database

        #return result


        message = room_id + "$"
        message += "Welcome to the room!" + "@" + " You are the host." + "@"
        message += "Here, we play " + GAME_ID_TO_NAME[game_id] + "."

        return message
