import sqlite3
import datetime
import random
import sys
sys.path.append('__HOME__/team079/rooms_infra/Python_Files')
import helpers

db = '__HOME__/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "PushUps"}


# Returns:
#           1 = everything ok
#           -1 = leave room (go back to main screen)
#
#

def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])
        password = str(args['password'])


        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        helpers.create_db(conn, c)
        result = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchall()

        # c.execute('''DROP TABLE users''')

        # c.execute('''DELETE FROM rooms''')
        # c.execute('''DELETE FROM games''')
        # c.execute('''DELETE FROM users''')
        # c.execute('''DELETE FROM push_ups''')

        # conn.commit()
        # conn.close()
        # return "ok"

        if len(result) == 0:
            conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
            c = conn.cursor()  # move cursor into database (allows us to execute commands)
            c.execute('''CREATE TABLE IF NOT EXISTS users (username text, room_id int, game_id int, last_ping timestamp, password text);''')
            c.execute('''INSERT into users VALUES (?,?,?,?,?);''', (username, -1, -1, datetime.datetime.now(), password))
            conn.commit()  # commit commands
        else:
            pass


        # Check if they need to be kicked out of a room

        #Check if anyone else needs to be kicked (because they haven't pinged in 10 seconds)

        helpers.check_online()

        c.execute("UPDATE users SET last_ping = ? WHERE username = ?", (str(datetime.datetime.now()), username))
        conn.commit()
        # for leave_user in need_to_leave:
        #     gone_offline(leave_user)

        result = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchall()

        room_id = result[0][1]
        conn.commit()  # commit commands
        conn.close()  # close connection to database

        if room_id == -1:
            return "-1" # = leave room (go back to main screen)
        else:
            #this user doesn't need to leave, but some others might... they will find out when they ping.
            return "1" # = everything ok


###################
