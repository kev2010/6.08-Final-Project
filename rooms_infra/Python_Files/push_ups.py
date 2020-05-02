import sqlite3
db = '__HOME__/project.db'
GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "PushUps"}

def request_handler(request):
    if request['method'] == "POST":
        args = request['form']
        username = str(args['username'])
        score = int(args['score'])

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        result = c.execute('''SELECT * FROM users WHERE username = ?''', (username,)).fetchall()
        room_id = result[1]

        result = c.execute('''SELECT * FROM push_ups WHERE username = ?''', (username,)).fetchall()

        if len(result) == 0: #never submitted a score for this game
            c.execute('''INSERT into push_ups VALUES (?,?,?);''',(room_id, username, score))
        else:
            current_score = result[0][2]

            if score > current_score:
                c.execute('''UPDATE push_ups SET score = ? WHERE username = ?;''', (score, username))

        conn.commit()  # commit commands
        conn.close()  # close connection to database

        return "Updated!"

    elif request['method'] == "GET":
        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)
        c.execute('''CREATE TABLE IF NOT EXISTS push_ups (room_id text, username text, score int);''')
        return request

        username = ""


        result = c.execute('''SELECT * FROM users WHERE username = ?''', (username,)).fetchall()
        room_id = result[1]

        result = c.execute('''SELECT * FROM push_ups WHERE room_id = ?''', (room_id,))
        result.sort(key=lambda x: x[2])


        conn.commit()  # commit commands
        conn.close()  # close connection to database

        leaderboard = ""

        for r in result:
            leaderboard += r[1] + " with score " + str(r[2]) + "\n"

        return leaderboard
