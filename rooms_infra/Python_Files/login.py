import sqlite3
# from Utils.py import *
import datetime

db = '__HOME__/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "Tichu"}

def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])

        create_db()
        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)
        c.execute('''INSERT into users VALUES (?,?,?,?);''', (username, -1, -1, datetime.datetime.now()))
        conn.commit()  # commit commands
        conn.close()  # close connection to database

        return "Hello user "+username+", you are online!"



def create_db():
    #only run once
    conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)
    c.execute('''CREATE TABLE IF NOT EXISTS users (username text, room_id int, game_id int, last_ping timestamp);''')
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (room_id text, host_username text, capacity int, game_id int, open_time timestamp);''')
    c.execute('''CREATE TABLE IF NOT EXISTS games (game_id int, room_id int, capacity int, start_time timestamp);''')
    conn.commit()  # commit commands
    conn.close()  # close connection to database