"""
PokerAPI handles POST/GET requests.
"""

import sqlite3
import random
import sys
sys.path.append('__HOME__/team079/poker-game')
from poker_actions import *
from room_actions import *
from render_game import *
from settings import *

#   Putting these in settings breaks the server... not sure why imports don't work
players_db = '__HOME__/team079/poker-game/players.db'
state_db = '__HOME__/team079/poker-game/state.db'
frames_db = '__HOME__/team079/poker-game/frames.db'

#   TODO: Make these functions take in database name string parameters
#   TODO: Optimize query calls (there are a lot of redundant "get all players" queries)
#   TODO: Potentially make a function for passing action? Does it relate to checking/calling/etc.
#   TODO: Make a function for legal actions?
#   TODO: Adjust "frames" for multiple step actions?

def request_handler(request):
    """
    Handles POST/GET requests for the poker game server. Assumes the POST/GET
    requests provide the following information:

    POST: user={user: str}&action={action: str}&amount={amount:str of int}&room_id={room_id: str}
    GET: param => user={user: str}
    
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
    #   Initialize the players_table SQL database
    conn_players = sqlite3.connect(players_db)
    c_player = conn_players.cursor()
    c_player.execute('''CREATE TABLE IF NOT EXISTS players_table 
                        (user text, bal int, bet int, invested int, 
                        cards text, position int, room_id text);''')
    
    #   Initialize the states_table SQL database
    conn_state = sqlite3.connect(state_db)
    c_state = conn_state.cursor()
    c_state.execute('''CREATE TABLE IF NOT EXISTS states_table 
                        (deck text, board text, dealer int, action
                        int, pot int, room_id text);''')

    #   Initialize the frames_table SQL database
    conn_frames = sqlite3.connect(frames_db)
    c_frame = conn_frames.cursor()
    c_frame.execute('''CREATE TABLE IF NOT EXISTS frames_table 
                        (state text, time timestamp, room_id text);''')

    game_state = ""
    if request['method'] == 'GET':
        get_type = request["values"]["type"]
        if get_type == "actions":
            game_state = get_actions_handler(request, c_player, c_state, c_frame)
        elif get_type == "spectate":
            game_state = get_spectate_handler(request, c_player, c_state, c_frame)
    elif request['method'] == 'POST':
        game_state = post_handler(request, c_player, c_state, c_frame)

    #   TODO: Figure out if this is the right order of commit/close
    conn_players.commit()
    conn_players.close()
    conn_state.commit()
    conn_state.close()
    conn_frames.commit()
    conn_frames.close()
    return game_state


def get_actions_handler(request, players_cursor, states_cursor, frames_cursor):
    """
    Handles a GET request as defined in the request_handler function.
    Returns a string representing the possible actions the user
    can take.

    Args:
        request (dict): maps request params to corresponding values
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table

    Returns:
        A string with the following format:
            size$action_1@action_2@param1@param2@param3@action_3@...
        Example with 25/50 blinds and stack sizes of 1000. Currently
        pre-flop and action is on UTG.
            7$call@raise@100@950@1000@fold@leave@
    """
    user = request["values"]["user"]
    room_id = request["values"]["room_id"]

    users_query = '''SELECT * FROM players_table 
                     WHERE room_id = ? 
                     ORDER BY position ASC;'''
    users = players_cursor.execute(users_query, (room_id,)).fetchall()
    query = '''SELECT * FROM states_table WHERE room_id = ?;'''
    game_state  = states_cursor.execute(query, (room_id,)).fetchall()[0]
    frames_query = '''SELECT * FROM frames_table WHERE room_id = ?;'''
    frames = frames_cursor.execute(frames_query, (room_id,)).fetchall()

    possible_actions = []
    if len(game_state) == 0:  #  game hasn't started yet
        possible_actions = ["leave"]
        if users[0][USERNAME] == user:
            possible_actions.append("start")
    elif len(frames) == 1:  #  all frames are done processing
        possible_actions = []
        if is_check_legal(users, game_state, user):
            possible_actions.append("check")
        if is_call_legal(users, game_state, user):
            possible_actions.append("call")
        bet_legal, min_bet, max_bet, all_in = is_bet_legal(users, game_state, user)
        if bet_legal:
            possible_actions.extend(["bet", str(min_bet), str(max_bet), str(all_in)])
        raise_legal, min_raise, max_raise, all_in = is_raise_legal(users, game_state, user)
        if raise_legal:
            possible_actions.extend(["raise", str(min_raise), str(max_raise), str(all_in)])
        if is_fold_legal(users, game_state, user):
            possible_actions.append("fold")
        
        possible_actions.append("leave")

    return str(len(possible_actions)) + "$" + "@".join(possible_actions) + "@"

    # if users[0][USERNAME] == user and len(game_state) == 0:
    #   possible_actions = ["start"]
      
    #   return str(len(possible_actions)) + "$" + "@".join(possible_actions) + "@"
    # else:
    #   game_action = game_state[0][ACTION]
    #   user_query = '''SELECT * FROM players_table WHERE user = ?;'''
    #   user_position = players_cursor.execute(user_query, (user,)).fetchall()[0][POSITION]
    #   if game_action == user_position:
    #     possible_actions = ["leave", "check", "call", "bet", "raise", "fold"]
    #     return str(len(possible_actions)) + "$" + "@".join(possible_actions) + "@"
    #   else:
    #     possible_actions = ["leave"]
    #     return str(len(possible_actions)) + "$" + "@".join(possible_actions) + "@"


def get_spectate_handler(request, players_cursor, states_cursor, frames_cursor):
    frames_query = '''SELECT * FROM frames_table 
                      ORDER BY time ASC;'''
    all_frames = frames_cursor.execute(frames_query).fetchall()
    # relevant_frames = []

    # for frame in all_frames:
    #     two_seconds_ago = datetime.datetime.now() - datetime.timedelta(seconds = 2)
    #     if frame[TIME] >= two_seconds_ago:  #   this means if this frame is newer
    #         relevant_frames.append(frame)

    # if len(relevant_frames) == 0:   #   we are too late
    #     relevant_frames = all_frames[-1]    #   we just take the most recent frame

    #   Delete all frames older than 2 seconds if there are >1 frames
    if len(all_frames) > 1:
        one_second_ago = datetime.datetime.now() - datetime.timedelta(seconds = 2)
        delete_frames = '''DELETE FROM frames_table WHERE time < ?'''
        frames_cursor.execute(delete_frames, (one_second_ago,))

    #   Get all the frames again
    frames_query = '''SELECT * FROM frames_table 
                      ORDER BY time ASC;'''
    all_frames = frames_cursor.execute(frames_query).fetchall()
    #   Return the oldest frame's state
    return all_frames[0][STATE]


def post_handler(request, players_cursor, states_cursor, frames_cursor):
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

    update_frames(frames_cursor)
    return display_frames(frames_cursor)

