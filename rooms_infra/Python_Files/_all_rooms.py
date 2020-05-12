import sqlite3

db = '__HOME__/project.db'

GAME_ID_TO_NAME = {0: "Poker", 1: "Blackjack", 2: "PushUps"}


def request_handler(request):

    if request['method'] == "GET":

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        # c.execute('''DELETE FROM push_ups''')
        # c.execute('''DELETE FROM games''')
        # c.execute('''DELETE FROM users''')

        result = c.execute('''SELECT * FROM rooms''').fetchall()
        conn.commit()  # commit commands
        conn.close()  # close connection to database

        return result
