import sys
sys.path.append('__HOME__/team079/poker-game')
from settings import *
from render_game import *
from game_logic import *
from legal_checks import *


#   TODO: TEST THIS
def check(players_cursor, states_cursor, user):
    """
    Handles a poker check request. Passes the turn to the next player or
    goes to the next stage if checking is a legal action. Assumes the 
    board has either 3, 4, or 5 cards.

    Checking is legal if:
        1. The action is on the user
        2. If the stage is post-flop, then there are no bets present at
            the table.
        3. If the stage is pre-flop, then everyone has limped to the big 
            blind, and the current action is on the big blind.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Raises:
        ValueError: if action is not on the user or checking is illegal
    """
    players_query = '''SELECT * FROM players_table ORDER BY position ASC;'''
    players = players_cursor.execute(players_query).fetchall()
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()[0]

    #   Make sure action is on the user
    game_action = game_state[ACTION]
    user_query = '''SELECT * FROM players_table WHERE user = ?;'''
    user_position = players_cursor.execute(user_query, (user,)).fetchall()[0][POSITION]
    if game_action != user_position:
        raise ValueError

    #   Make sure checking is a legal option
    #   Checking is legal only if there are no bets yet or in the big blind special case
    bets_query = '''SELECT * FROM players_table WHERE bet > ?'''
    bets = players_cursor.execute(bets_query, (0,)).fetchall()
    #   Find max bet
    max_bet = 0
    for better in bets:
        if better[BET] > max_bet:
            max_bet = better[BET]
    #   See if it's big blind special case
    preflop = len(game_state[BOARD]) == 0
    big_blind_pos = (game_state[DEALER] + 2) % len(players)
    big_blind_special = preflop and user_position == big_blind_pos and max_bet == BIG_BLIND
    if bets and not big_blind_special:
        raise ValueError
    
    #   Take care of BB special case if necessary
    if big_blind_special:
        next_stage(players_cursor, states_cursor, 0, user)
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
                next_stage(players_cursor, states_cursor, len(board_cards), user)
                break
            elif i != 0:
                next_player = players[position]
                if next_player[CARDS] != '' and next_player[BALANCE] > 0:
                    update_action = ''' UPDATE states_table
                                        SET action = ? '''
                    states_cursor.execute(update_action, (position,))
                    FRAMES.append(display_game(players_cursor, states_cursor, user))
                    break

#   TODO: TEST THIS
def call(players_cursor, states_cursor, user):
    """
    Handles a poker call request. Calls the previous bet and passes
    the turn to the next player or goes to the next stage if calling
    is a legal action. Assumes the board has either 0, 3, 4, or 5 cards.

    Calling is legal if:
        1. The action is on the user
        2. There is at least one non-zero bet present at the table

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Raises:
        ValueError: if action is not on the user or calling is illegal 
    """
    players_query = '''SELECT * FROM players_table ORDER BY position ASC;'''
    players = players_cursor.execute(players_query).fetchall()
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()[0]

    #   Make sure action is on the user
    game_action = game_state[ACTION]
    user_query = '''SELECT * FROM players_table WHERE user = ?;'''
    player = players_cursor.execute(user_query, (user,)).fetchall()[0]
    user_position = player[POSITION]
    if game_action != user_position:
        raise ValueError

    #   Make sure calling is a legal option
    #   Calling is legal only if there are bets present
    bets_query = '''SELECT * FROM players_table WHERE bet > ?'''
    bets = players_cursor.execute(bets_query, (0,)).fetchall()
    if len(bets) == 0:
        raise ValueError
    
    #   Find the max bet that user has to call
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
                        WHERE user = ?'''
    players_cursor.execute(update_chips, (new_bal, new_bet, new_invested, user))

    #   Update the pot size
    update_pot = ''' UPDATE states_table
                     SET pot = ?'''
    states_cursor.execute(update_pot, (game_state[POT] + bet_delta,))
    
    #   Update action
    found = False
    for i in range(1, len(players)):
        position = (user_position + i) % len(players)
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
                                SET action = ? '''
            states_cursor.execute(update_action, (position,))
            found = True
            FRAMES.append(display_game(players_cursor, states_cursor, user))
            break
    
    if not found:
        board_cards = game_state[BOARD].split(',')
        if len(board_cards) == 1:   #  empty case
            board_cards = []
        FRAMES.append(display_game(players_cursor, states_cursor, user))
        next_stage(players_cursor, states_cursor, len(board_cards), user)


def bet(players_cursor, states_cursor, user, amount):
    """
    Handles a poker bet request. Bets the specified amount and passes
    the turn to the next player if betting is a legal action. Assumes 
    the board has either 0, 3, 4, or 5 cards.

    Betting is legal if:
        1. The action is on the user
        2. There are no bets present at the table
        3. The user is betting at least the size of the big blind

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
        amount (int): a non-zero amount to bet. Must be a size that is
            legal in poker
    
    Raises:
        TODO: customize errors
        ValueError: if action is not on the user, betting is illegal,
            or the size is illegal 
    """
    players_query = '''SELECT * FROM players_table ORDER BY position ASC;'''
    players = players_cursor.execute(players_query).fetchall()
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()[0]

    #   Make sure action is on the user
    #   TODO: perhaps make this a function?
    game_action = game_state[ACTION]
    user_query = '''SELECT * FROM players_table WHERE user = ?;'''
    player = players_cursor.execute(user_query, (user,)).fetchall()[0]
    user_position = player[POSITION]
    if game_action != user_position:
        raise ValueError

    #   Make sure betting is a legal option
    #   Betting is legal only if there are no bets present
    #   Otherwise, it would be considered raising
    bets_query = '''SELECT * FROM players_table WHERE bet > ?'''
    bets = players_cursor.execute(bets_query, (0,)).fetchall()
    if bets:
        raise ValueError

    #   Make sure bet size is legal (at least the big blind)
    if amount < BIG_BLIND:
        raise ValueError

    #   Update player state with the bet
    new_bal = player[BALANCE] - amount
    new_invested = player[INVESTED] + amount
    update_chips = ''' UPDATE players_table
                        SET bal = ?,
                            bet = ?,
                            invested = ?
                        WHERE user = ?'''
    players_cursor.execute(update_chips, (new_bal, amount, new_invested, user))

    #   Update the pot size
    update_pot = ''' UPDATE states_table
                     SET pot = ?'''
    states_cursor.execute(update_pot, (game_state[POT] + amount,))
    
    #   Update action
    for i in range(1, len(players)):
        position = (user_position + i) % len(players)
        next_player = players[position]
        if next_player[CARDS] != '' and next_player[BALANCE] > 0: 
            update_action = ''' UPDATE states_table
                                SET action = ? '''
            states_cursor.execute(update_action, (position,))
            FRAMES.append(display_game(players_cursor, states_cursor, user))
            break


def raise_bet(players_cursor, states_cursor, user, amount):
    """
    Handles a poker raise request. Raises to the specified amount 
    and passes the turn to the next player if raising is legal. 
    Assumes the board has either 0, 3, 4, or 5 cards.

    Raising is legal if:
        1. The action is on the user
        2. There is at least one non-zero bet present at the table
        3. The user is raising by at least the previous raise,
            unless it is an all-in. For example, if the previous
            raise was from 2bb to 6bb, any raise >=10bb is legal.
        4. If another player has gone all-in, this user closes
            the action, and the all-in size is not at least the
            previous raise size, then raising is illegal.
    
    Note that for now, condition 4 is not checked.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
        amount (int): a non-zero amount to raise to. Must be a 
            size that is legal in poker
    
    Raises:
        TODO: customize errors
        ValueError: if action is not on the user, raising is illegal,
            or the size to raise to is illegal 
    """
    players_query = '''SELECT * FROM players_table ORDER BY position ASC;'''
    players = players_cursor.execute(players_query).fetchall()
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()[0]

    #   Make sure action is on the user
    #   TODO: perhaps make this a function?
    game_action = game_state[ACTION]
    user_query = '''SELECT * FROM players_table WHERE user = ?;'''
    player = players_cursor.execute(user_query, (user,)).fetchall()[0]
    user_position = player[POSITION]
    if game_action != user_position:
        raise ValueError

    #   Make sure raising is a legal option
    #   Raising is legal only if there are bets present
    bets_query = '''SELECT * FROM players_table WHERE bet > ?'''
    bets = players_cursor.execute(bets_query, (0,)).fetchall()
    if len(bets) == 0:
        raise ValueError

    #   Make sure raise size is legal
    #   Must be raising BY at least the previous raise (except for all-in)
    #   TODO: perhaps split the all-in case from raise?
    if amount != player[BALANCE] + player[BET]:  #  All-in
        #   Find the largest and 2nd largest bet
        max_bet = 0
        for better in bets:
            if better[BET] > max_bet:
                max_bet = better[BET]
        
        second_max_bet = 0
        if len(bets) != 1:
            #   TODO: Maybe don't copy? 
            other_bets = [i for i in bets if i != max_bet]
            for better in other_bets:
                if better[BET] > second_max_bet:
                    second_max_bet = better[BET]
        
        if amount < 2*max_bet - second_max_bet:
            raise ValueError

    #   Update player state with the raise
    new_bal = player[BALANCE] + player[BET] - amount
    raise_delta = amount - player[BET]
    new_invested = player[INVESTED] + raise_delta
    update_chips = ''' UPDATE players_table
                        SET bal = ?,
                            bet = ?,
                            invested = ?
                        WHERE user = ?'''
    players_cursor.execute(update_chips, (new_bal, amount, new_invested, user))

    #   Update the pot size
    update_pot = ''' UPDATE states_table
                     SET pot = ?'''
    states_cursor.execute(update_pot, (game_state[POT] + raise_delta,))
    
    #   Update action
    #   TODO: perhaps combine all the "update action" code together?
    for i in range(1, len(players)):
        position = (user_position + i) % len(players)
        next_player = players[position]
        if next_player[CARDS] != '' and next_player[BALANCE] > 0: 
            update_action = ''' UPDATE states_table
                                SET action = ? '''
            states_cursor.execute(update_action, (position,))
            FRAMES.append(display_game(players_cursor, states_cursor, user))
            break


def fold(players_cursor, states_cursor, user):
    """
    Handles a poker fold request. Folds the user's hand and 
    passes the turn to the next player if folding is legal.

    Folding is legal if:
        1. The action is on the user
        2. There is at least one non-zero bet present at the table

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Raises:
        TODO: customize errors
        ValueError: if action is not on the user or folding
            is illegal
    """
    players_query = '''SELECT * FROM players_table ORDER BY position ASC;'''
    players = players_cursor.execute(players_query).fetchall()
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()[0]

    #   Make sure action is on the user
    game_action = game_state[ACTION]
    user_query = '''SELECT * FROM players_table WHERE user = ?;'''
    player = players_cursor.execute(user_query, (user,)).fetchall()[0]
    user_position = player[POSITION]
    if game_action != user_position:
        raise ValueError

    #   Make sure folding is a legal option
    #   Folding is legal only if there are bets present
    bets_query = '''SELECT * FROM players_table WHERE bet > ?'''
    bets = players_cursor.execute(bets_query, (0,)).fetchall()
    if len(bets) == 0:
        raise ValueError
    
    update_cards = ''' UPDATE players_table
                       SET cards = ?
                       WHERE user = ?'''
    players_cursor.execute(update_cards, ('', user))

    users_playing_query = '''SELECT * FROM players_table WHERE cards != ?;'''
    users_playing = players_cursor.execute(users_playing_query, ('',)).fetchall()
    #   If all but one player folded, then give the pot and start new hand
    if len(users_playing) == 1:
        winner_name = users_playing[0][USERNAME]
        FRAMES.append(display_game(players_cursor, states_cursor, user))
        distribute_pots(players_cursor, states_cursor, user)
    #   Otherwise, we just pass the action to next player (similar to calling)
    else:
        #   Find the max bet
        max_bet = 0
        for better in bets:
            if better[BET] > max_bet:
                max_bet = better[BET]
            
        found = False
        for i in range(1, len(players)):
            position = (user_position + i) % len(players)
            next_player = players[position]
            #  user has cards, isn't all-in, and hasn't bet the right amount condition
            if next_player[CARDS] != '' and next_player[BET] != max_bet and next_player[BALANCE] > 0: 
                update_action = ''' UPDATE states_table
                                    SET action = ? '''
                states_cursor.execute(update_action, (position,))
                found = True
                FRAMES.append(display_game(players_cursor, states_cursor, user))
                break

        if not found:
            board_cards = game_state[BOARD].split(',')
            if len(board_cards) == 1:   #  empty case
                board_cards = []
            FRAMES.append(display_game(players_cursor, states_cursor, user))
            next_stage(players_cursor, states_cursor, len(board_cards), user)
