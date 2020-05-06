import sys
sys.path.append('__HOME__/team079/poker-game')
from settings import *


def is_check_legal(players_cursor, states_cursor, user):
    """
    Determines whether a check action is legal given the state
    of the game.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Returns:
        True if checking is legal.
    """
    pass


def is_call_legal(players_cursor, states_cursor, user):
    """
    Determines whether the call action is legal given the state
    of the game.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Returns:
        True if calling is legal.
    """
    pass


def is_bet_legal(players_cursor, states_cursor, user):
    """
    Determines if betting is legal given the state of the game.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Returns:
        A length three tuple where the first entry is a boolean
        indicating if betting is legal, and the second and third
        entries are the min bet and max bet allowed, respectively.
        Note that the second and third entries are 0 if first entry
        is false.
    """
    pass


def is_raise_legal(players_cursor, states_cursor, user):
    """
    Determines if raising is legal given the state of the game.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Returns:
        A length three tuple where the first entry is a boolean
        indicating if raising is legal, and the second and third
        entries are the min raise to and max raise to allowed, 
        respectively. Note that the second and third entries are 
        0 if first entry is false.
    """
    pass


def is_fold_legal(players_cursor, states_cursor, user):
    """
    Determines whether the fold action is legal given the state
    of the game.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Returns:
        True if folding is legal.
    """
    pass


def is_on_user(players_cursor, states_cursor, user):
    """
    Determines whether the action is on the user.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Returns:
        True if action is on user.
    """
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()[0]

    #   Make sure action is on the user
    game_action = game_state[ACTION]
    user_query = '''SELECT * FROM players_table WHERE user = ?;'''
    user_position = players_cursor.execute(user_query, (user,)).fetchall()[0][POSITION]
    return game_action == user_position