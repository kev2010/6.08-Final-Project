"""Checks if certain poker actions are legal given a game state.

This module contains functions that check if certain poker actions
are allowed given the state of the players and game.
"""
import sys
sys.path.append('__HOME__/team079/poker-game')
from settings import *


def is_check_legal(players, game_state, user):
    """
    Determines whether a check action is legal given the state
    of the game.

    Args:
        players (list of tuples): list of players as defined by the SQL player
            database (check request_handler.py file specification). The players
            should be sorted in ascending order of position.
        game_state (tuple): a game state as defined by the SQL state database in
            request_handler.py.
        user (str): non-empty username to check the action for.
    
    Returns:
        True if checking is legal.
    """
    user_position = [p[POSITION] for p in players if p[USERNAME] == user][0]

    #   Make sure action is on the user
    if not is_on_user(players, game_state, user):
        return False
    
    #   Checking is legal only if there are no bets yet or in the big blind special case
    bets = [p for p in players if p[BET] > 0]
    #   Find max bet
    max_bet = 0
    for better in bets:
        if better[BET] > max_bet:
            max_bet = better[BET]
    #   See if it's big blind special case
    preflop = len(game_state[BOARD]) == 0
    big_blind_pos = (game_state[DEALER] + 2) % len(players)
    big_blind_special = preflop and user_position == big_blind_pos and max_bet == BIG_BLIND
    return not bets or big_blind_special
    

def is_call_legal(players, game_state, user):
    """
    Determines whether the call action is legal given the state
    of the game.

    Args:
        players (list of tuples): list of players as defined by the SQL player
            database (check request_handler.py file specification). The players
            should be sorted in ascending order of position.
        game_state (tuple): a game state as defined by the SQL state database in
            request_handler.py.
        user (str): non-empty username to check the action for.
    
    Returns:
        True if calling is legal.
    """
    #   Make sure action is on the user
    if not is_on_user(players, game_state, user):
        return False

    #   Calling is legal only if there are bets present
    bets = [p for p in players if p[BET] > 0]
    return len(bets) > 0


def is_bet_legal(players, game_state, user):
    """
    Determines if betting is legal given the state of the game.

    Args:
        players (list of tuples): list of players as defined by the SQL player
            database (check request_handler.py file specification). The players
            should be sorted in ascending order of position.
        game_state (tuple): a game state as defined by the SQL state database in
            request_handler.py.
        user (str): non-empty username to check the action for.
    
    Returns:
        A length four tuple where the first entry is a boolean
        indicating if betting is legal, and the second and fourth
        entries are the min bet and max bet allowed, respectively.
        The third entry is the 2nd max bet allowed since players
        are not allowed to have a stack size of less than a big 
        blind left after betting. Note that the second, third and
        fourth entries are 0 if first entry is false.

        E.g. the blinds are 25/50, betting is legal, and user has
            a stack size of 1000. The return would be 
            (True, 50, 950, 1000). The user is not allowed to bet
            between 950 and 1000 since that would leave less than
            a BB left.
    """
    if not is_on_user(players, game_state, user):
        return (False, 0, 0, 0)
    
    #   Betting is legal only if there are no bets present
    #   Otherwise, it would be considered raising
    bets = [p for p in players if p[BET] > 0]
    if bets:
        return (False, 0, 0, 0)
    else:
        player = [p for p in players if p[USERNAME] == user][0]
        return (True, 
                BIG_BLIND, player[BALANCE] - BIG_BLIND, player[BALANCE])


def is_raise_legal(players, game_state, user):
    """
    Determines if raising is legal given the state of the game.

    Args:
        players (list of tuples): list of players as defined by the SQL player
            database (check request_handler.py file specification). The players
            should be sorted in ascending order of position.
        game_state (tuple): a game state as defined by the SQL state database in
            request_handler.py.
        user (str): non-empty username to check the action for.
    
    Returns:
        A length four tuple where the first entry is a boolean
        indicating if raising is legal, and the second and fourth
        entries are the min raise to and max raise to allowed, 
        respectively. The third entry is the 2nd max raise to allowed 
        since players are not allowed to have a stack size of less 
        than a big blind left after betting (Read is_bet_legal spec
        to see an example). Note that the second, third and fourth 
        entries are 0 if first entry is false.
    """
    if not is_on_user(players, game_state, user):
        return (False, 0, 0, 0)

    #   Raising is legal only if there are bets present
    bets = [p for p in players if p[BET] > 0]
    if len(bets) == 0:
        return (False, 0, 0, 0)
    else:
        #   Find the largest and 2nd largest bet
        max_bet = 0
        for better in bets:
            if better[BET] > max_bet:
                max_bet = better[BET]
        
        second_max_bet = 0
        if len(bets) != 1:
            #   TODO: Maybe don't copy? 
            other_bets = [i for i in bets if i[BET] != max_bet]
            for better in other_bets:
                if better[BET] > second_max_bet:
                    second_max_bet = better[BET]
        delta = max_bet - second_max_bet
        player = [p for p in players if p[USERNAME] == user][0]
        min_raise = max_bet + (delta if delta > BIG_BLIND else BIG_BLIND)
        return (True, 
                min_raise, player[BALANCE] - BIG_BLIND, player[BALANCE])


def is_fold_legal(players, game_state, user):
    """
    Determines whether the fold action is legal given the state
    of the game.

    Args:
        players (list of tuples): list of players as defined by the SQL player
            database (check request_handler.py file specification). The players
            should be sorted in ascending order of position.
        game_state (tuple): a game state as defined by the SQL state database in
            request_handler.py.
        user (str): non-empty username to check the action for.
    
    Returns:
        True if folding is legal.
    """
    #   Same case as calling
    return is_call_legal(players, game_state, user)


def is_on_user(players, game_state,  user):
    """
    Determines whether the action is on the user.

    Args:
        players (list of tuples): list of players as defined by the SQL player
            database (check request_handler.py file specification). The players
            should be sorted in ascending order of position.
        game_state (tuple): a game state as defined by the SQL state database in
            request_handler.py.
        user (str): non-empty username to check the action for.
    
    Returns:
        True if action is on user.
    """
    #   Make sure action is on the user
    game_action = game_state[ACTION]
    user_position = [p[POSITION] for p in players if p[USERNAME] == user][0]
    return game_action == user_position
