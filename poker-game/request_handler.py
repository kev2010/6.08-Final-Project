import sqlite3
import random
import sys
sys.path.append('__HOME__/team079/poker-game')
from poker_actions import *
from room_actions import *

players_db = '__HOME__/team079/poker-game/players.db'
state_db = '__HOME__/team079/poker-game/state.db'

#   TODO: Make these functions take in database name string parameters
#   TODO: Optimize query calls (there are a lot of redundant "get all players" queries)
#   TODO: Potentially make a function for passing action? Does it relate to checking/calling/etc.
#   TODO: Make a function for legal actions?
#   TODO: Adjust "frames" for multiple step actions?

def request_handler(request):
    """
    Handles POST/GET requests for the poker game server. Assumes the POST/GET
    requests provide the following information:

    POST: user={user: str}&action={action: str}&amount={amount:str of int}
    GET: None
    
    Returns a string representing the state of the poker game. The string is
    in the form of a JSON in the following format:

        game_state:
            {
                "players": [
                    {
                        "user": kev2010, 
                        "bal": 850,
                        "bet": 150,
                        "invested": 150,
                        "cards": "Ah,Kd"
                        "position": 0
                    },
                    {
                        "user": baptiste, 
                        "bal": 950,
                        "bet": 50,
                        "cards": ""
                        "position": 1
                    },
                    ...
                ],
                "state": {
                    "board": "Ah,7d,2s",
                    "dealer": 3,
                    "action": 1,
                    "pot": 225"
                }
            }

    The game_state provides a list of players with the corresponding
    information. Some fields in the player information are private,
    such as the cards if player object is not the user sending the
    post request. The game_state also contains the state with the board
    cards, the current dealer position, who's action it's on, and 
    the total pot size.

    Args:
        request (dict): maps request params to corresponding values
    
    Returns:
        A JSON string representing the players and state of 
        the game as defined above
    """
    #   Initialize the players_table and states_table SQL database
    # create_player_database(players_db)
    # create_state_database(state_db)
    conn_players = sqlite3.connect(players_db)
    c_player = conn_players.cursor()
    c_player.execute('''CREATE TABLE IF NOT EXISTS players_table 
                        (user text, bal int, bet int, invested int, 
                        cards text, position int);''')
    conn_state = sqlite3.connect(state_db)
    c_state = conn_state.cursor()
    c_state.execute('''CREATE TABLE IF NOT EXISTS states_table 
                        (deck text, board text, dealer int, action
                        int, pot int);''')

    game_state = ""
    if request['method'] == 'GET':
        user = request["values"]["user"]
        game_state = get_handler(user, request, c_player, c_state)
    elif request['method'] == 'POST':
        game_state = post_handler(request, c_player, c_state)

    #   TODO: Figure out if this is the right order of commit/close
    conn_players.commit()
    conn_players.close()
    conn_state.commit()
    conn_state.close()
    return game_state


def get_handler(user, request, players_cursor, states_cursor):
    """
    Handles a GET request as defined in the request_handler function.
    Returns a string representing the game state as defined in
    request_handler.

    Args:
        request (dict): maps request params to corresponding values
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table

    Returns:
        TODO: A JSON string representing the players and state of 
        the game as defined above

        Currently returns the game state as specified by the
        display_game function
    """
    
    users_query = '''SELECT * FROM players_table;'''
    users = players_cursor.execute(users_query).fetchall()
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()
    if users[0][USERNAME] == user and len(game_state) == 0:
      possible_actions = ["start"]
      
      return str(len(possible_actions)) + "$" + "@".join(possible_actions) + "@"
    else:
      game_action = game_state[0][ACTION]
      user_query = '''SELECT * FROM players_table WHERE user = ?;'''
      user_position = players_cursor.execute(user_query, (user,)).fetchall()[0][POSITION]
      if game_action == user_position:
        possible_actions = ["leave", "check", "call", "bet", "raise", "fold"]
        return str(len(possible_actions)) + "$" + "@".join(possible_actions) + "@"
      else:
        possible_actions = ["leave"]
        return str(len(possible_actions)) + "$" + "@".join(possible_actions) + "@"      
 
      

    #return display_game(players_cursor, states_cursor)


def post_handler(request, players_cursor, states_cursor):
    """
    Handles a POST request as defined in the request_handler function.
    Returns a string representing the game state as defined in
    request_handler.

    Args:
        request (dict): maps request params to corresponding values
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table

    Returns:
        A JSON string representing the players and state of 
        the game as defined above
    """
    #   Get the user, action, and amount from the POST request
    user = request['form']['user']
    action = request['form']['action']
    amount = int(request['form']['amount'])

    #   Split actions based on type of request
    #   TODO: implement other actions
    if action == "join":
        join_game(players_cursor, states_cursor, user)
    elif action == "start":
        start_game(players_cursor, states_cursor, user)
    elif action == "leave":
        leave_game(players_cursor, states_cursor, user)
    elif action == "check":
        check(players_cursor, states_cursor, user)
    elif action == "call":
        call(players_cursor, states_cursor, user)
    elif action == "bet":
        bet(players_cursor, states_cursor, user, amount)
    elif action == "raise":
        raise_bet(players_cursor, states_cursor, user, amount)
    elif action == "fold":
        fold(players_cursor, states_cursor, user)
    else:
        return "Requested action not recognized!"

    return render_frames()

