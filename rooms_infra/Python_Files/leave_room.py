import sqlite3
from Utils import *

db = '__HOME__/team079/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "Tichu"}


def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        #First get the room_id
        room_id = c.execute("SELECT room_id FROM users WHERE username=\""+username+"\"")[0][0]

        #Get the room data. Are they the host?
        result = c.execute("SELECT * FROM rooms WHERE room_id="+str(room_id))
        host_username = result[0][1]
        is_host = host_username == username

        #Update the capacity of the room
        capacity = result[0][2]
        c.execute("UPDATE rooms SET capacity = "+str(capacity)+" WHERE room_id =" + str(room_id))

        conn.commit()  # commit commands
        conn.close()  # close connection to database

        if is_host:
            delete_room(room_id)

        else:
            return "You have successfully left. \n Welcome back to the lobby."


