import sqlite3

db = '__HOME__/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "Tichu"}

def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])
        room_id = int(args['room_id'])

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        # ping(username)

        result = c.execute("SELECT * FROM rooms WHERE room_id="+str(room_id))
        if len(result) == 0:
            return "Invalid room id!"

        game_id = int(result[0][3])
        host = result[0][1]
        capacity = result[0][2]

        c.execute("UPDATE rooms SET capacity = "+str(capacity+1)+" WHERE room_id =" + str(room_id))

        description_of_all_activities = "Welcome to room" + str(room_id) + ". The host is" + host + "\n"
        description_of_all_activities += "Here, the activity is " + GAME_ID_TO_NAME[game_id]

        conn.commit()  # commit commands
        conn.close()  # close connection to database

        return description_of_all_activities

    elif request['method'] == "GET":

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        result = c.execute('''SELECT * FROM rooms''')

        room_descriptions = ""

        for r in result:
            room_descriptions += str(r[0])
            room_descriptions += ", hosted by " + str(r[1])
            room_descriptions += ", capacity " + str(r[2])
            room_descriptions += ", game: " + GAME_ID_TO_NAME[int(r[3])]
            # room_descriptions += ", game: " + str(r[3])
            room_descriptions += "\n"

        conn.commit()  # commit commands
        conn.close()  # close connection to database

        return room_descriptions
