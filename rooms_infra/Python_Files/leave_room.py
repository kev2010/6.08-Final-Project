import sqlite3
#from Utils import *
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

        #First get the room_id
        result = c.execute('''SELECT * FROM users WHERE username = ?;''', (username,)).fetchall()
        room_id = result[0][1]
        # result = c.execute('''SELECT * FROM rooms''').fetchall()
        # return result

        #Get the room data. Are they the host?
        result = c.execute('''SELECT * FROM rooms WHERE room_id = ?;''', (room_id,)).fetchall()
        host_username = result[0][1]
        is_host = host_username == username

        #Update the capacity of the room
        capacity = result[0][2]
        c.execute('''UPDATE rooms SET capacity = ? WHERE room_id = ?;''', (str(capacity-1), str(room_id)))

        c.execute("UPDATE users SET room_id = -1 WHERE username =?", (username,))
        c.execute("UPDATE users SET game_id = -1 WHERE username =?", (username,))

        conn.commit()  # commit commands
        conn.close()  # close connection to database

        if is_host:
            helpers.delete_room(room_id)
            return "Room deleted because host left."

        else:
            return "You have successfully left. \n Welcome back to the lobby."
