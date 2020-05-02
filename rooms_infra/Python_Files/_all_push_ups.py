import sqlite3

db = '__HOME__/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "PushUps"}


def request_handler(request):
    # if request['method'] == "POST":
    #     args = request['form']
    #     username = str(args['username'])
    #     room_id = str(args['room_id'])
    #
    #     conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
    #     c = conn.cursor()  # move cursor into database (allows us to execute commands)
    #
    #     # ping(username)
    #
    #     result = c.execute('''SELECT * FROM rooms WHERE room_id = ?;''', (room_id,)).fetchall()
    #     try:
    #         game_id = int(result[0][3])
    #         host = result[0][1]
    #         capacity = result[0][2]
    #     except:
    #         conn.commit()  # commit commands
    #         conn.close()  # close connection to database
    #         return "Invalid room id !"
    #
    #     #        game_id = int(result[0][3])
    #     #        host = result[0][1]
    #     #        capacity = result[0][2]
    #
    #     c.execute('''UPDATE rooms SET capacity = ? WHERE room_id = ?;''', (str(capacity + 1), room_id))
    #     # c.execute("UPDATE rooms SET capacity = "+str(capacity+1)+" WHERE room_id =" + room_id)
    #     c.execute('''UPDATE users SET room_id = ? WHERE username = ?;''', (room_id, username))
    #     c.execute('''UPDATE users SET game_id = ? WHERE username = ?;''', (game_id, username))
    #
    #     description_of_all_activities = "Welcome to the room!" + "@" + " The host is " + host + "." + "@"
    #     description_of_all_activities += "Here, we play " + GAME_ID_TO_NAME[game_id] + "."
    #
    #     conn.commit()  # commit commands
    #     conn.close()  # close connection to database
    #
    #     return description_of_all_activities

    if request['method'] == "GET":

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        result = c.execute('''SELECT * FROM push_ups''').fetchall()
        conn.commit()  # commit commands
        conn.close()  # close connection to database

        return result
