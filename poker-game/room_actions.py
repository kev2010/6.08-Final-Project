import sys
sys.path.append('__HOME__/team079/poker-game')
from settings import *
from game_logic import *

def join_game(players_cursor, states_cursor, user):
    """
    Handles a join game request. Adds the user to the game if it
    is not full. Otherwise, rejects the user from joining.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Raises:
        TODO: Custom errors for joining
        ValueError: if player is already in the game
                    or the game is full
    """
    #   Make sure player isn't already in the game
    joined_query = '''SELECT * FROM players_table WHERE user = ?;'''
    joined = players_cursor.execute(joined_query, (user,)).fetchall()
    if len(joined) > 0:
        #   TODO: Return proper message for already in game
         raise ValueError

    #   Check if the game is already full
    players_query = '''SELECT * FROM players_table;'''
    players = players_cursor.execute(players_query).fetchall()
    if len(players) == MAX_PLAYERS:
        #   TODO: Return proper message for joining full game
        raise ValueError

    #   Since the game is not full, add the player to the game
    insert_player = '''INSERT into players_table VALUES (?,?,?,?,?,?);'''
    players_cursor.execute(insert_player,
                           (user, STARTING_STACK, 0, 0, "", len(players)))
    
    FRAMES.append(display_game(players_cursor, states_cursor, user))


def start_game(players_cursor, states_cursor, user):
    """
    Handles a start game request. Starts the game if the request
    was sent by the host, and there are at least two players.
    
    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Raises:
        ValueError: if the user trying to start is not the host
    """
    users_query = '''SELECT * FROM players_table;'''
    users = players_cursor.execute(users_query).fetchall()
    if users[0][USERNAME] == user:
        #   Insert a game state entry into the states_table
        deck = ",".join(cards)
        board = ""
        dealer = random.randint(0, len(users) - 1)
        action = (dealer + 3) % len(users)
        pot = 0

        new_state = '''INSERT into states_table 
                    VALUES (?,?,?,?,?);'''
        states_cursor.execute(new_state, (deck, board, dealer, action, pot))
        start_new_hand(players_cursor, states_cursor, dealer, user)
    else:
        raise ValueError


def leave_game(players_cursor, states_cursor, user):
    """
    Handles a leave game request. Deletes the user from the game.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    """
    leave_query = '''DELETE FROM players_table WHERE user = ?'''
    players_cursor.execute(leave_query, (user,))
    FRAMES.append(display_game(players_cursor, states_cursor, user))

