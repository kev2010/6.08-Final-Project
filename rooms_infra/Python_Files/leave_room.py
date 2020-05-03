import sqlite3
#from Utils import *

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
            delete_room(room_id)
            return "Room deleted because host left."

        else:
            return "You have successfully left. \n Welcome back to the lobby."






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
        gone_offline(r[0], r[1], r[2])
        to_leave.append(r[0])

    return to_leave

def gone_offline(username, room_id, game_id):
    #remove username from the server, and makes according actions

    conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)



    if room_id != -1:
        result2 = c.execute("SELECT * FROM rooms WHERE room_id=?", (room_id,)).fetchall()

        host_name = result2[0][1]
        capacity = result2[0][2]


        if host_name == username or capacity == 1:
            delete_room(room_id)

        else:
            c.execute("UPDATE rooms SET capacity = ? WHERE room_id =?", (capacity-1, room_id))
            c.execute("UPDATE games SET capacity = ? WHERE room_id =?", (capacity-1, room_id))
            c.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            # return "deleted" + username

    conn.commit()  # commit commands
    conn.close()  # close connection to database

def delete_room(room_id):
    conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)

    result = c.execute("SELECT * FROM users WHERE room_id=?", (room_id,)).fetchall()
    game_id = result[0][2]
    for r in result:
        #remove them from game and room
        user = r[0]
        c.execute("UPDATE users SET game_id = ? WHERE username =?", (-1, user))
        c.execute("UPDATE users SET room_id = ? WHERE username =?", (-1, user))
        conn.commit()
    #delete the game and room
    c.execute("DELETE FROM games WHERE game_id=?", (game_id,))
    c.execute("DELETE FROM rooms WHERE room_id=?", (room_id,))
    c.execute("DELETE FROM push_ups WHERE room_id=?", (room_id,))

    conn.commit()  # commit commands
    conn.close()  # close connection to database
