"""Renders the poker game for clients to process.

This module provides a way for clients to access the game
state from the Poker API. Serves as a conversion from
the data in the SQL database to a JSON output.
"""

import json
import sys
import datetime
sys.path.append('__HOME__/team079/poker-game')
from settings import *


def display_game(players_cursor, states_cursor, user, room_id):
    """
    Returns the poker game state in a properly formatted JSON
    string. The return format is as follows:

        {
            "state": {
                "deck": "Jh,8s,..."
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
                    "cards": "Ts,Td",
                    "position": 1,
                    "room_id": "123"
                },
                ...
            ]
        }
    
    There can be multiple players, but there is only one state
    for the poker game.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): user who sent the request
        room_id (str): the id for the room user is in
    
    Returns:
        A string of the state of the game, formatted as described
        above
    """
    # players_query = '''SELECT * FROM players_table;'''
    # players = players_cursor.execute(players_query).fetchall()
    # result = "players:\n"
    # for p in players:
    #     cards = str(p[CARDS]) if p[USERNAME] == user else ""
    #     player_info = "(" + str(p[USERNAME]) + ", " + str(p[BALANCE]) + ", " + str(p[BET]) + ", " + cards + ", " + str(p[POSITION]) + ")"
    #     result += player_info + "\n"
    #     # result += str(p) + "\n"
        

    # result += "\nstate:\n"
    # current_state_query = '''SELECT * FROM states_table;'''
    # state = states_cursor.execute(current_state_query).fetchall()
    # for s in state:
    #     result += "(" + str(s[BOARD]) + ", " + str(s[DEALER]) + ", " + str(s[ACTION]) + ", " + str(s[POT]) + ")"
    #     # result += str(s) + "\n"
    
    # return result
    r = {"state": {}, "players": {}}
    query = '''SELECT * FROM states_table WHERE room_id = ?;'''
    states_cursor.execute(query, (room_id,))
    r["state"] = [dict((states_cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in states_cursor.fetchall()]

    players_query = '''SELECT * FROM players_table WHERE room_id = ?;'''
    players_cursor.execute(players_query, (room_id,))
    users = [dict((players_cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in players_cursor.fetchall()]
    r["players"] = users
    
    json_output = json.dumps(r)
    return json_output


def update_frames(frames_cursor, room_id):
    """
    Updates the frames of the game state.

    Args:
        frames_cursor (SQL cursor): cursor for the frames_table
        room_id (str): the id for the room to get frames from
    """
    counter = 0
    for frame in FRAMES:    #   frame is json string
        update_states = ''' INSERT into frames_table 
                            VALUES (?,?,?); '''
        time = datetime.datetime.now() + datetime.timedelta(seconds=counter)
        frames_cursor.execute(update_states, (frame, time, room_id))
        counter += 2


def display_frames(frames_cursor, room_id):
    """
    Displays all the stored frames of the game state in the room
    with the given room_id. Should only be used for debugging
    since this exposes private elements (e.g. the deck, other
    player's cards, etc.)

    Args:
        frames_cursor (SQL cursor): cursor for the frames_table
        room_id (str): the id for the room to get frames from
    """
    query = '''SELECT * FROM frames_table WHERE room_id = ?;'''
    frames = frames_cursor.execute(query, (room_id,)).fetchall()

    counter = 1
    result = ""
    for state in frames:
        result += "FRAME" + str(counter) + "\n"
        result += str(state) + "\n\n"
        counter += 1
    
    return result
    
