import sqlite3
import datetime

db = '__HOME__/project.db'

def create_db(conn, c):
    #only run once
    # conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
    # c = conn.cursor()  # move cursor into database (allows us to execute commands)
    c.execute('''CREATE TABLE IF NOT EXISTS users (username text, room_id int, game_id int, last_ping timestamp, password text);''')
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (room_id text, host_username text, capacity int, game_id int, open_time timestamp);''')
    c.execute('''CREATE TABLE IF NOT EXISTS games (game_id int, room_id int, capacity int, start_time timestamp);''')
    c.execute('''CREATE TABLE IF NOT EXISTS push_ups (room_id text, username text, score int);''')

    # conn.commit()  # commit commands
    # conn.close()  # close connection to database


def check_online(conn, c):
    #checks for everyone in the users db and removes and deletes from games/rooms if they haven't been active for >10s

    result = c.execute('''SELECT * FROM users WHERE last_ping < ?''', (datetime.datetime.now() - datetime.timedelta(seconds=30),)).fetchall()
    #
    # conn.commit()  # commit commands
    # conn.close()  # close connection to database
    to_leave = []
    for r in result:
        gone_offline(r[0], r[1], r[2], conn, c)
        to_leave.append(r[0])

    return to_leave

def gone_offline(username, room_id, game_id, conn, c):
    #remove username from the server, and makes according actions

    # conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
    # c = conn.cursor()  # move cursor into database (allows us to execute commands)
    #


    if room_id != -1:
        result2 = c.execute("SELECT * FROM rooms WHERE room_id=?", (room_id,)).fetchall()

        host_name = result2[0][1]
        capacity = result2[0][2]


        if host_name == username or capacity == 1:
            delete_room(room_id, conn, c)
            c.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()

        else:
            c.execute("UPDATE rooms SET capacity = ? WHERE room_id =?", (capacity-1, room_id))
            c.execute("UPDATE games SET capacity = ? WHERE room_id =?", (capacity-1, room_id))
            c.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            # return "deleted" + username
    else:
        c.execute("DELETE FROM users WHERE username=?", (username,))
        res = c.execute("SELECT * FROM rooms WHERE host_username=?", (username,)).fetchall()
        for r in res:
            delete_room(r[0], conn, c)
        conn.commit()
    #
    # conn.commit()  # commit commands
    # conn.close()  # close connection to database

def delete_room(room_id, conn, c):
    # conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
    # c = conn.cursor()  # move cursor into database (allows us to execute commands)

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
    # conn.close()  # close connection to database
