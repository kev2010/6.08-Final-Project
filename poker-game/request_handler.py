"""Poker API Request Handler

The Poker API handles POST/GET requests from clients. This module
serves as the abstraction of poker games. All poker games are
represented as follows:

    Players:
        (user:str, balance:int, bet:int, invested:int, cards:str, 
        position:int, room_id:str)
        ...
    Game state:
        (deck:str, board:str, dealer:int, action:int, pot:int,
        room_id:str)
    Frames:
        (state:text, time:timestamp, room_id:str)
        ...

These entries are all stored in a players, states, and frames
SQL database, respectively. Each entry in the players database
stores relevant information about that user in the poker game.
The game state entry stores information related to the game
logic. Each entry in the frames database stores a JSON string
of players and a game state at a timestamp.

Note that the frames database is a combination of snapshots of
the players and game_state databases. The purpose of storing frames
is for clients to get a "user friendly" sequence of game states.

Example:
    If all players go all in preflop, instead of only returning 
    the end game state, a sequence of intermediary "frames" 
    (e.g. the flop, turn, river, and pot distribution) will be
    returned for clients to process.

The abstraction function for this ADT is as follows:

    AF(players, game_state) = a poker game with players in
        "players", where each player has two hole cards
        specified by player[cards], a balance of player[balance],
        and a bet of player[bet]. For the state of the game,
        the deck is in game_state[deck], the board is in
        game_state[board], the pot is in game_state[pot],
        the dealer is in game_state[dealer], and the
        action is on player with position game_state[action].

Note that the Poker API currently supports multiple rooms. Clients
can make POST/GET requests to the Poker API to simulate these
multiple poker games. The request_handler specification outlines
the possible interactions clients can make with the abstracted
poker game.

Attributes:
    players_db (str): file location for the players SQL database
    state_db (str): file location for the state SQL database
    frames_db (str): file location for the frames SQL database

Todo:
    * Make these functions take in database name string parameters?
    * Optimize query calls (there are a lot of redundant "get all 
        players" queries) 
    * Potentially make a function for passing action? Does it 
        relate to checking/calling/etc.
"""

import sqlite3
import random
import json
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


def request_handler(request):
    """
    Handles POST/GET requests for the poker game server. Assumes the POST/GET
    requests provide the following information:

    POST: user={str}&action={str}&amount={str of int}&room_id={str}
    GET: param => user={str}&type={str}&room_id={str}

    Each POST/GET request requires a room_id parameter since these
    requests will only affect the player in the specified room_id. This
    allows multiple rooms to host different poker games since actions in
    one room_id will not affect a room with a different room_id.
    
    POST requests are for when players want to make actions in the poker
    game. Therefore, POSTs only return a string saying "Success!" to clients.
    The following actions are currently supported:
        
        1. "join" - lets any user join the poker game with given room_id
        2. "start" - lets the host start a poker game with given room_id
        3. "leave" - lets any user leave the poker game with given room_id
        4. "check" - user performs a poker "check" action in the game
        5. "call" - user performs a poker "call" action in the game
        6. "bet" - user performs a poker "bet" action in the game with
            the specified amount
        7. "raise" - user performs a poker "raise" action in the game to
            the specified amount
        8. "fold" - user performs a poker "fold" action in the game
    
    GET requests are for observing the poker game. The return type depends
    on the type specified in the GET request. The following types are 
    currently supported:

        1. "actions" - gets all the legal actions a specified player can
            make. Returns a string with all possible legal actions.
        2. "spectate" - gets a single frame of the poker game. Returns
            a string JSON containing a snapshot of players and the game
            state.

    Args:
        request (dict): maps request params to corresponding values
    
    Returns:
        A string containing the relevant information for the POST/GET
        request.
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
        
#    if request["form"]["type"] == "get_actions":
#        game_state = get_actions_handler(request, c_player, c_state, c_frame)
#    elif request["form"]["type"] == "make_action":

    conn_players.commit()
    conn_players.close()
    conn_state.commit()
    conn_state.close()
    conn_frames.commit()
    conn_frames.close()
    return game_state


def get_actions_handler(request, players_cursor, states_cursor, frames_cursor):
    """
    Handles a GET actions request as defined in the request_handler function.
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
        This means that the player can 7 possible actions: call a bet, 
        raise to a size in the interval [100, 950] U [1000], fold, or
        leave the game.

        Only the "bet" and "raise" actions specify 3 parameters. Read the
        specifications for "is_bet_legal()" and "is_raise_legal()" to
        see how and why parameters are returned.
    """
    user = request["values"]["user"]
    room_id = request["values"]["room_id"]
    
#    user = request["form"]["user"]
#    room_id = request["form"]["room_id"]
    
    ## CHANGED , then reset

    users_query = '''SELECT * FROM players_table 
                     WHERE room_id = ? 
                     ORDER BY position ASC;'''
    users = players_cursor.execute(users_query, (room_id,)).fetchall()
    query = '''SELECT * FROM states_table WHERE room_id = ?;'''
    
    try:
        game_state  = states_cursor.execute(query, (room_id,)).fetchall()[0]
    except:
        game_state = ()

    frames_query = '''SELECT * FROM frames_table WHERE room_id = ?;'''
    frames = frames_cursor.execute(frames_query, (room_id,)).fetchall()

    possible_actions = []
    if len(game_state) == 0:  #  game hasn't started yet
        if users[0][USERNAME] == user:
            possible_actions.append("start")
    elif len(frames) >= 1:  #  all frames are done processing
        possible_actions = []
        if is_check_legal(users, game_state, user):
            possible_actions.append("check")
        if is_call_legal(users, game_state, user):
            possible_actions.append("call")
        bet_legal, min_bet, max_bet, all_in = is_bet_legal(users, game_state, user)
        if bet_legal:
            possible_actions.append("bet@" + str(min_bet) + "@" + str(max_bet) + "@" + str(all_in))
        raise_legal, min_raise, max_raise, all_in = is_raise_legal(users, game_state, user)
        if raise_legal:
            possible_actions.append("raise@" + str(min_raise) + "@" + str(max_raise) + "@" + str(all_in))
        if is_fold_legal(users, game_state, user):
            possible_actions.append("fold")
        
        possible_actions.append("leave")
       
    else:
        return "Frames have length " + str(len(frames)) + " which is not 1"

    #return "5$start@bet@100@200@400@leave@fold@raise@50@150@500"

    return str(len(possible_actions)) + "$" + "@".join(possible_actions) 

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
    """
    Handles a GET spectate request as defined in the request_handler function.
    Returns a JSON string representing a singular frame of the game.

    Args:
        request (dict): maps request params to corresponding values
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table

    Returns:
        Returns the poker game state in a properly formatted JSON
        string. The return format is as follows:

        {
            "state": {
                "board": "Ah,7d,2s",
                "dealer": 3,
                "action": 1,
                "pot": 225",
                "room_id": "123"
            },
            "players": [
                {
                    "user": kev2010, 
                    "bal": 850,
                    "bet": 150,
                    "invested": 150,
                    "cards": "Ah,Kd",
                    "position": 0,
                    "room_id": "123"
                },
                {
                    "user": baptiste, 
                    "bal": 950,
                    "bet": 50,
                    "invested": 50,
                    "cards": "hidden",
                    "position": 1,
                    "room_id": "123"
                },
                ...
            ]
        }
    """
    room_id = request["values"]["room_id"]
    frames_query = '''SELECT * FROM frames_table 
                      WHERE room_id = ?
                      ORDER BY time ASC;'''
    all_frames = frames_cursor.execute(frames_query, (room_id,)).fetchall()
    two_seconds_ago = datetime.datetime.now() - datetime.timedelta(seconds = 2)
    relevant_frames_query = '''SELECT * FROM frames_table 
                               WHERE room_id = ? AND time >= ?
                               ORDER BY time ASC;''' 
    relevant_frames = frames_cursor.execute(relevant_frames_query, (room_id, two_seconds_ago)).fetchall()

    if len(relevant_frames) == 0:   #   we are too late
        relevant_frames = [all_frames[-1]]    #   we just take the most recent frame
        #   Delete the rest of the frames
        older = relevant_frames[0][TIME]
        delete_frames = '''DELETE FROM frames_table WHERE time < ? AND room_id = ?'''
        frames_cursor.execute(delete_frames, (older, room_id))
    else:
        two_seconds_ago = datetime.datetime.now() - datetime.timedelta(seconds = 2)
        delete_frames = '''DELETE FROM frames_table WHERE time < ? AND room_id = ?'''
        frames_cursor.execute(delete_frames, (two_seconds_ago, room_id))
    
    #   Hide the deck and other player cards
    to_display = relevant_frames[0][STATE]
    data = json.loads(to_display)
    del data["state"][0]["deck"]
    for p in data["players"]:
        if p["user"] != request["values"]["user"]:
            if p["cards"] != "":
                p["cards"] = "hidden"
    
    to_display = json.dumps(data)

    return to_display
    # return all_frames[0][STATE]

    # #   Delete all frames older than 2 seconds if there are >1 frames
    # if len(all_frames) > 1:
    #     two_seconds_ago = datetime.datetime.now() - datetime.timedelta(seconds = 2)
    #     delete_frames = '''DELETE FROM frames_table WHERE time < ? AND room_id = ?'''
    #     frames_cursor.execute(delete_frames, (two_seconds_ago, room_id))

    # #   Get all the frames again
    # frames_query = '''SELECT * FROM frames_table
    #                   WHERE room_id = ?
    #                   ORDER BY time ASC;'''
    # all_frames = frames_cursor.execute(frames_query, (room_id,)).fetchall()
    # #   Return the oldest frame's state
    # return all_frames[0][STATE]


def post_handler(request, players_cursor, states_cursor, frames_cursor):
    """
    Handles a POST request as defined in the request_handler function.

    Args:
        request (dict): maps request params to corresponding values
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table

    Returns:
        A string "Success!" if the action was processed correctly.
        Otherwise, "Requested action not recognized!" is returned
        if the POST request contains an action not currently
        supported.
    """
    #   Get the user, action, and amount from the POST request
    user = request['form']['user']
    action = request['form']['action']
    amount = int(request['form']['amount'])
    room_id = request['form']['room_id']

    #   Split actions based on type of request
    #   TODO: implement other actions
    
    if action == "join":
        join_game(players_cursor, states_cursor, user, room_id)
    elif action == "start" or action[0:5] == "start":
        start_game(players_cursor, states_cursor, user, room_id)
        
    elif action == "leave" or action[0:5] == "leave":
        leave_game(players_cursor, states_cursor, user, room_id)
    elif action == "check":
        check(players_cursor, states_cursor, user, room_id)
    elif action == "call":
        call(players_cursor, states_cursor, user, room_id)
    elif action == "bet":
        bet(players_cursor, states_cursor, user, amount, room_id)
    elif action == "raise":
        raise_bet(players_cursor, states_cursor, user, amount, room_id)
    elif action == "fold":
        fold(players_cursor, states_cursor, user, room_id)
    else:
        return action + " action not recognized!"

    update_frames(frames_cursor, room_id)
    # return display_frames(frames_cursor, room_id)
    return "Success!" 
