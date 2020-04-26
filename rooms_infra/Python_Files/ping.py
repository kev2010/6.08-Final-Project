import sqlite3
import datetime

# import importlib.util
# spec = importlib.util.spec_from_file_location("utils", "var/jail/home/team079/team079/rooms_infra/utils/helpers.py")
# Utils = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(Utils)
#
# var/jail/home/username
#
# f
# import sys
# sys.path.insert(0, 'var/jail/home/team079/team079/rooms_infra/utils/')
# from utils import helpers

# from utils.helpers import check_online

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

        result = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchall()

        if len(result) == 0:
            conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
            c = conn.cursor()  # move cursor into database (allows us to execute commands)
            c.execute('''INSERT into users VALUES (?,?,?,?);''', (username, -1, -1, datetime.datetime.now()))
            conn.commit()  # commit commands

        c.execute("UPDATE users SET last_ping = ? WHERE username = ?", (str(datetime.datetime.now()), username))

        # Check if they need to be kicked out of a room

        #Check if anyone else needs to be kicked (because they haven't pinged in 10 seconds)
        return check_online()

        # for leave_user in need_to_leave:
        #     gone_offline(leave_user)

        result = c.execute("SELECT * FROM users WHERE username=(?,)", (username,)).fetchall()

        conn.commit()  # commit commands
        conn.close()  # close connection to database

        room_id = result[0][1]

        if room_id == -1:
            return "-1" # = leave room (go back to main screen)
        else:
            #this user doesn't need to leave, but some others might... they will find out when they ping.
            return "1" # = everything ok


###################

def check_online():
    #checks for everyone in the users db and removes and deletes from games/rooms if they haven't been active for >10s
    conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)

    result = c.execute('''SELECT * FROM users WHERE last_ping < ?''', (datetime.datetime.now() - datetime.timedelta(seconds=30),)).fetchall()

    conn.commit()  # commit commands
    conn.close()  # close connection to database


    to_leave = []

    for r in result:
        return gone_offline(r[0])
        to_leave.append(r[0])

    return to_leave

def gone_offline(username):
    #remove username from the server, and makes according actions

    conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)

    result = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchall()

    room_id = result[0][1]
    game_id = result[0][2]

    result2 = c.execute("SELECT * FROM rooms WHERE room_id=?", (room_id,)).fetchall()

    host_name = result2[0][1]
    capacity = result2[0][2]


    if host_name == username or capacity == 1:
        return delete_room(room_id)

    else:
        c.execute("UPDATE rooms SET capacity = ? WHERE room_id =?", (capacity-1, room_id))
        c.execute("UPDATE games SET capacity = ? WHERE room_id =?", (capacity-1, room_id))
        c.execute("DELETE FROM users WHERE username=?", (username,))

    conn.commit()  # commit commands
    conn.close()  # close connection to database

def delete_room(room_id):
    conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)

    result = c.execute("SELECT * FROM users WHERE room_id=?", (room_id,)).fetchall()
    for r in result:
        #remove them from game and room
        user = r[0]
        c.execute("UPDATE users SET game_id = ? WHERE username =?", (-1, user))
        c.execute("UPDATE users SET room_id = ? WHERE username =?", (-1, user))

    return "hi"
    #delete the game and room
    c.execute("DELETE FROM games WHERE room_id=?", (room_id,))
    c.execute("DELETE FROM rooms WHERE room_id=?", (room_id,))

    conn.commit()  # commit commands
    conn.close()  # close connection to database
