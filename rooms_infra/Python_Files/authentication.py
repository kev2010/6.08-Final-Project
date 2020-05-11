import sqlite3

db = '__HOME__/project.db'

def request_handler(request):
    if request['method'] == "GET":
        username = request['values']['username']
        password = request['values']['password']

        conn = sqlite3.connect(db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)

        result = c.execute('''SELECT * FROM users WHERE username = ?''', (username,)).fetchall()
        conn.commit()  # commit commands
        conn.close()  # close connection to database

        if len(result)>0 and result[0][4] == password:
            return 1

        return 0