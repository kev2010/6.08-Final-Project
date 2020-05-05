import sqlite3
import sys
sys.path.append('__HOME__/team079/poker-game')
from settings import *

def display_game(players_cursor, states_cursor, user):
    """
    Returns the poker game state in a properly formatted string.
    The return format is as follows:
        
        players:
        (user:str, bal:int, bet:int, cards:str, position:int)
        ...

        state:
        (deck:str, board:str, dealer:int, action:int, pot:int)
    
    There can be multiple players, but there is only one state
    for the poker game. The following is an example string that
    could be returned.

        players:
        ('kev2010', 950, 0, '2s,9s', 0)
        ('jasonllu', 950, 0, 'Jh,8s', 1)
        ('baptiste', 950, 0, '7d,4c', 2)

        state:
        ('Js,3s,8h, ...', 'Qd,2h,9h,3d', 0, 1, 150)
    
    Note that the deck in the state will have more cards, as
    indicated by the "...".

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): user who sent the request
    
    Returns:
        A string of the state of the game, formatted as described
        above
    """
    #   TODO: Return proper JSON message of the state of the game
    players_query = '''SELECT * FROM players_table;'''
    players = players_cursor.execute(players_query).fetchall()
    result = "players:\n"
    for p in players:
        cards = str(p[CARDS]) if p[USERNAME] == user else ""
        player_info = "(" + str(p[USERNAME]) + ", " + str(p[BALANCE]) + ", " + str(p[BET]) + ", " + cards + ", " + str(p[POSITION]) + ")"
        result += player_info + "\n"
        # result += str(p) + "\n"
        

    result += "\nstate:\n"
    current_state_query = '''SELECT * FROM states_table;'''
    state = states_cursor.execute(current_state_query).fetchall()
    for s in state:
        result += "(" + str(s[BOARD]) + ", " + str(s[DEALER]) + ", " + str(s[ACTION]) + ", " + str(p[POT]) + ")"
        # result += str(s) + "\n"
    
    return result


def render_frames():
    """
    Renders the frames of the game state.
    """
    counter = 1
    result = ""
    for frame in FRAMES:
        result += "FRAME " + str(counter) + ":\n"
        result += frame + "\n"
        counter += 1
    return result
