"""Handles user poker game actions

This module deals with poker actions (checking, calling, betting, etc.).
All of the functions interact with the players and states SQL database.
"""

import sys
sys.path.append('__HOME__/team079/poker-game')
from settings import *
from render_game import *
from game_logic import *
from legal_checks import *



def check(players_cursor, states_cursor, user, room_id):
    """
    Handles a poker check request. Passes the turn to the next player or
    goes to the next stage. Assumes that checking is a legal action.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username who sent the request
        room_id (str): the id for the room user is in
    """
    players_query = '''SELECT * FROM players_table WHERE room_id = ? ORDER BY position ASC;'''
    players = players_cursor.execute(players_query, (room_id,)).fetchall()
    query = '''SELECT * FROM states_table WHERE room_id = ?;'''
    game_state  = states_cursor.execute(query, (room_id,)).fetchall()[0]

    #   See if it's big blind special case
    user_query = '''SELECT * FROM players_table WHERE user = ? AND  room_id = ?;'''
    user_position = players_cursor.execute(user_query, (user, room_id)).fetchall()[0][POSITION]
    bets_query = '''SELECT * FROM players_table WHERE bet > ? AND  room_id = ?'''
    bets = players_cursor.execute(bets_query, (0, room_id)).fetchall()
    #   Find max bet
    max_bet = 0
    for better in bets:
        if better[BET] > max_bet:
            max_bet = better[BET]
    preflop = len(game_state[BOARD]) == 0
    big_blind_pos = (game_state[DEALER] + 2) % len(players)
    big_blind_special = preflop and user_position == big_blind_pos and max_bet == BIG_BLIND
    
    #   Take care of BB special case if necessary
    if big_blind_special:
        next_stage(players_cursor, states_cursor, 0, user, room_id)
    else:
        #   Otherwise, we pass the action to the next player
        #   that has cards and isn't all-in, or end the action
        for i in range(1, len(players)):
            position = (user_position + i) % len(players)
            #   If this user is the small blind, then the original 
            #   user has ended the action
            if position == (game_state[DEALER] + 1) % len(players):
                board_cards = game_state[BOARD].split(',')
                if len(board_cards) == 1:   #  empty case
                    board_cards = []
                next_stage(players_cursor, states_cursor, len(board_cards), user, room_id)
                break
            elif i != 0:
                next_player = players[position]
                if next_player[CARDS] != '' and next_player[BALANCE] > 0:
                    update_action = ''' UPDATE states_table
                                        SET action = ?
                                        WHERE room_id = ?'''
                    states_cursor.execute(update_action, (position, room_id))
                    FRAMES.append(display_game(players_cursor, states_cursor, user, room_id))
                    break


def call(players_cursor, states_cursor, user, room_id):
    """
    Handles a poker call request. Calls the previous bet and passes
    the turn to the next player or goes to the next stage. Assumes 
    that calling is legal.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username who sent the request
        room_id (str): the id for the room user is in
    """
    players_query = '''SELECT * FROM players_table WHERE room_id = ? ORDER BY position ASC;'''
    players = players_cursor.execute(players_query, (room_id,)).fetchall()
    query = '''SELECT * FROM states_table WHERE room_id = ?;'''
    game_state  = states_cursor.execute(query, (room_id,)).fetchall()[0]
    user_query = '''SELECT * FROM players_table WHERE user = ? AND  room_id = ?;'''
    player = players_cursor.execute(user_query, (user, room_id)).fetchall()[0]
    
    #   Find the max bet that user has to call
    bets_query = '''SELECT * FROM players_table WHERE bet > ? AND room_id = ?'''
    bets = players_cursor.execute(bets_query, (0, room_id)).fetchall()
    max_bet = 0
    for better in bets:
        if better[BET] > max_bet:
            max_bet = better[BET]
    to_call = min(max_bet, player[BALANCE] + player[BET])  #  Min of bet and the user's chip stack
    #   Put the bet in front of the user
    new_bet = to_call
    new_bal = player[BALANCE] + player[BET] - to_call
    bet_delta = new_bet - player[BET]
    new_invested = player[INVESTED] + bet_delta
    update_chips = ''' UPDATE players_table
                        SET bal = ?,
                            bet = ?,
                            invested = ?
                        WHERE user = ?  AND 
                              room_id = ?'''
    players_cursor.execute(update_chips, (new_bal, new_bet, new_invested, user, room_id))

    #   Update the pot size
    update_pot = ''' UPDATE states_table
                     SET pot = ?
                     WHERE room_id = ?'''
    states_cursor.execute(update_pot, (game_state[POT] + bet_delta, room_id))
    
    #   Update action
    found = False
    for i in range(1, len(players)):
        position = (player[POSITION] + i) % len(players)
        next_player = players[position]
        #  user has cards, hasn't bet the right amount condition, and isn't all-in
        has_cards_wrong_bet = next_player[CARDS] != '' and next_player[BET] != max_bet and next_player[BALANCE] > 0
        #  NOTE: special case where everyone limps preflop
        #  TODO: perhaps this actually isn't a special case?
        preflop = len(game_state[BOARD]) == 0
        big_blind_pos = (game_state[DEALER] + 2) % len(players)
        big_blind_special = preflop and next_player[POSITION] == big_blind_pos and max_bet == BIG_BLIND 

        if has_cards_wrong_bet or big_blind_special: 
            update_action = ''' UPDATE states_table
                                SET action = ? 
                                WHERE room_id = ?'''
            states_cursor.execute(update_action, (position, room_id))
            found = True
            FRAMES.append(display_game(players_cursor, states_cursor, user, room_id))
            break
    
    if not found:
        board_cards = game_state[BOARD].split(',')
        if len(board_cards) == 1:   #  empty case
            board_cards = []
        FRAMES.append(display_game(players_cursor, states_cursor, user, room_id))
        next_stage(players_cursor, states_cursor, len(board_cards), user, room_id)


def bet(players_cursor, states_cursor, user, amount, room_id):
    """
    Handles a poker bet request. Bets the specified amount and passes
    the turn to the next player. Assumes betting is legal.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username who sent the request
        amount (int): a non-zero amount to bet. Must be a size that is
            legal in poker
        room_id (str): the id for the room user is in
    """
    players_query = '''SELECT * FROM players_table WHERE room_id = ? ORDER BY position ASC;'''
    players = players_cursor.execute(players_query, (room_id,)).fetchall()
    query = '''SELECT * FROM states_table WHERE room_id = ?;'''
    game_state  = states_cursor.execute(query, (room_id,)).fetchall()[0]
    user_query = '''SELECT * FROM players_table WHERE user = ? AND  room_id = ?;'''
    player = players_cursor.execute(user_query, (user, room_id)).fetchall()[0]

    #   Update player state with the bet
    new_bal = player[BALANCE] - amount
    new_invested = player[INVESTED] + amount
    update_chips = ''' UPDATE players_table
                        SET bal = ?,
                            bet = ?,
                            invested = ?
                        WHERE user = ? AND 
                              room_id = ?'''
    players_cursor.execute(update_chips, (new_bal, amount, new_invested, user, room_id))

    #   Update the pot size
    update_pot = ''' UPDATE states_table
                     SET pot = ?
                     WHERE room_id = ?'''
    states_cursor.execute(update_pot, (game_state[POT] + amount, room_id))
    
    #   Update action
    for i in range(1, len(players)):
        position = (player[POSITION] + i) % len(players)
        next_player = players[position]
        if next_player[CARDS] != '' and next_player[BALANCE] > 0: 
            update_action = ''' UPDATE states_table
                                SET action = ?
                                WHERE room_id = ?'''
            states_cursor.execute(update_action, (position, room_id))
            FRAMES.append(display_game(players_cursor, states_cursor, user, room_id))
            break


def raise_bet(players_cursor, states_cursor, user, amount, room_id):
    """
    Handles a poker raise request. Raises to the specified amount 
    and passes the turn to the next player. Assumes raising is legal.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
        amount (int): a non-zero amount to raise to. Must be a 
            size that is legal in poker
        room_id (str): the id for the room user is in
    """
    players_query = '''SELECT * FROM players_table WHERE room_id = ? ORDER BY position ASC;'''
    players = players_cursor.execute(players_query, (room_id,)).fetchall()
    query = '''SELECT * FROM states_table WHERE room_id = ?;'''
    game_state  = states_cursor.execute(query, (room_id,)).fetchall()[0]
    user_query = '''SELECT * FROM players_table WHERE user = ? AND  room_id = ?;'''
    player = players_cursor.execute(user_query, (user, room_id)).fetchall()[0]

    #   Update player state with the raise
    new_bal = player[BALANCE] + player[BET] - amount
    raise_delta = amount - player[BET]
    new_invested = player[INVESTED] + raise_delta
    update_chips = ''' UPDATE players_table
                        SET bal = ?,
                            bet = ?,
                            invested = ?
                        WHERE user = ? AND 
                              room_id = ?'''
    players_cursor.execute(update_chips, (new_bal, amount, new_invested, user, room_id))

    #   Update the pot size
    update_pot = ''' UPDATE states_table
                     SET pot = ?
                     WHERE room_id = ?'''
    states_cursor.execute(update_pot, (game_state[POT] + raise_delta, room_id))
    
    #   Update action
    #   TODO: perhaps combine all the "update action" code together?
    for i in range(1, len(players)):
        position = (player[POSITION] + i) % len(players)
        next_player = players[position]
        if next_player[CARDS] != '' and next_player[BALANCE] > 0: 
            update_action = ''' UPDATE states_table
                                SET action = ?
                                WHERE room_id = ?'''
            states_cursor.execute(update_action, (position, room_id))
            FRAMES.append(display_game(players_cursor, states_cursor, user, room_id))
            break


def fold(players_cursor, states_cursor, user, room_id):
    """
    Handles a poker fold request. Folds the user's hand and 
    passes the turn to the next player.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username who sent the request
        room_id (str): the id for the room user is in
    """
    players_query = '''SELECT * FROM players_table WHERE room_id = ? ORDER BY position ASC;'''
    players = players_cursor.execute(players_query, (room_id,)).fetchall()
    query = '''SELECT * FROM states_table WHERE room_id = ?;'''
    game_state  = states_cursor.execute(query, (room_id,)).fetchall()[0]
    user_query = '''SELECT * FROM players_table WHERE user = ? AND  room_id = ?;'''
    player = players_cursor.execute(user_query, (user, room_id)).fetchall()[0]
    
    update_cards = ''' UPDATE players_table
                       SET cards = ?
                       WHERE user = ? AND 
                             room_id = ?'''
    players_cursor.execute(update_cards, ('', user, room_id))

    users_playing_query = '''SELECT * FROM players_table WHERE cards != ? AND room_id = ?;'''
    users_playing = players_cursor.execute(users_playing_query, ('', room_id)).fetchall()
    #   If all but one player folded, then give the pot and start new hand
    if len(users_playing) == 1:
        FRAMES.append(display_game(players_cursor, states_cursor, user, room_id))
        distribute_pots(players_cursor, states_cursor, user, room_id)
    #   Otherwise, we just pass the action to next player (similar to calling)
    else:
        bets_query = '''SELECT * FROM players_table WHERE bet > ? AND room_id = ?'''
        bets = players_cursor.execute(bets_query, (0, room_id)).fetchall()
        #   Find the max bet
        max_bet = 0
        for better in bets:
            if better[BET] > max_bet:
                max_bet = better[BET]
            
        found = False
        for i in range(1, len(players)):
            position = (player[POSITION] + i) % len(players)
            next_player = players[position]
            #  user has cards, isn't all-in, and hasn't bet the right amount condition
            has_cards_wrong_bet = next_player[CARDS] != '' and next_player[BET] != max_bet and next_player[BALANCE] > 0
            #  NOTE: special case where everyone limps preflop
            #  TODO: perhaps this actually isn't a special case?
            preflop = len(game_state[BOARD]) == 0
            big_blind_pos = (game_state[DEALER] + 2) % len(players)
            big_blind_special = preflop and next_player[POSITION] == big_blind_pos and max_bet == BIG_BLIND 

            if has_cards_wrong_bet or big_blind_special:
                update_action = ''' UPDATE states_table
                                    SET action = ?
                                    WHERE room_id = ?'''
                states_cursor.execute(update_action, (position, room_id))
                found = True
                FRAMES.append(display_game(players_cursor, states_cursor, user, room_id))
                break

        if not found:
            board_cards = game_state[BOARD].split(',')
            if len(board_cards) == 1:   #  empty case
                board_cards = []
            FRAMES.append(display_game(players_cursor, states_cursor, user, room_id))
            next_stage(players_cursor, states_cursor, len(board_cards), user, room_id)
