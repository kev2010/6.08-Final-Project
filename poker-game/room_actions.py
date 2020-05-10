"""Handles player actions regarding the room.

This module handles actions that affect the state of the
room in a poker game (e.g. joining, leaving, starting
the game, etc.)

Todo:
    * Raise custom errors for joining/starting
"""

import sys
sys.path.append('__HOME__/team079/poker-game')
from settings import *
from game_logic import *


def join_game(players_cursor, states_cursor, user, room_id):
    """
    Handles a join game request. Adds the user to the game if it
    is not full. Otherwise, rejects the user from joining.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
        room_id (str): the id for the room user is in
    
    Raises:
        ValueError: if player is already in the game
                    or the game is full
    """
    #   Make sure player isn't already in the game
    joined_query = '''SELECT * FROM players_table WHERE user = ? AND room_id = ?;'''
    joined = players_cursor.execute(joined_query, (user, room_id)).fetchall()
    if len(joined) > 0:
        #   TODO: Return proper message for already in game
         raise KeyError

    #   Check if the game is already full
    players_query = '''SELECT * FROM players_table WHERE room_id = ?;'''
    players = players_cursor.execute(players_query, (room_id,)).fetchall()
    if len(players) == MAX_PLAYERS:
        #   TODO: Return proper message for joining full game
        raise ValueError

    #   Since the game is not full, add the player to the game
    insert_player = '''INSERT into players_table VALUES (?,?,?,?,?,?,?);'''
    players_cursor.execute(insert_player,
                           (user, STARTING_STACK, 0, 0, "", len(players), room_id))
    
    FRAMES.append(display_game(players_cursor, states_cursor, user, room_id))


def start_game(players_cursor, states_cursor, user, room_id):
    """
    Handles a start game request. Starts the game if the request
    was sent by the host, and there are at least two players.
    
    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
        room_id (str): the id for the room user is in
    
    Raises:
        ValueError: if the user trying to start is not the host
    """
    users_query = '''SELECT * FROM players_table WHERE room_id = ?;'''
    users = players_cursor.execute(users_query, (room_id,)).fetchall()
    if users[0][USERNAME] == user:
        #   Insert a game state entry into the states_table
        
        deck = ",".join(cards)
        board = ""
        dealer = random.randint(0, len(users) - 1)
        action = (dealer + 3) % len(users)
        pot = 0

        new_state = '''INSERT into states_table 
                    VALUES (?,?,?,?,?,?);'''
        states_cursor.execute(new_state, (deck, board, dealer, action, pot, room_id))
        start_new_hand(players_cursor, states_cursor, dealer, user, room_id)
        
    else:
        raise ValueError

def leave_game(players_cursor, states_cursor, user, room_id):
    """
    Handles a leave game request. Deletes the user from the game.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
        room_id (str): the id for the room user is in
    """
    leave_query = '''DELETE FROM players_table WHERE user = ? AND room_id = ?'''
    players_cursor.execute(leave_query, (user, room_id))
    FRAMES.append(display_game(players_cursor, states_cursor, user, room_id))

