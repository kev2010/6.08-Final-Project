import sqlite3
import random
# from databaseFuncs import *
players_db = '__HOME__/team079/poker-game/players.db'
state_db = '__HOME__/team079/poker-game/state.db'

#   Constants
MAX_PLAYERS = 3
SMALL_BLIND = 25
BIG_BLIND = 50
STARTING_STACK = 1000
all_ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
all_suits = ['s', 'c', 'd', 'h']
cards = {rank + suit for rank in all_ranks for suit in all_suits}
card_order_dict = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, 
                   "T":10, "J":11, "Q":12, "K":13, "A":14}

#   Player SQL DB indicies
USERNAME = 0
BALANCE = 1
BET = 2
INVESTED = 3
CARDS = 4
POSITION = 5

#   Game State SQL DB indicies
DECK = 0
BOARD = 1
DEALER = 2
ACTION = 3
POT = 4

#   TODO: Make these functions take in database name string parameters
#   TODO: Optimize query calls (there are a lot of redundant "get all players" queries)
#   TODO: Potentially make a function for passing action? Does it relate to checking/calling/etc.
#   TODO: Make a function for legal actions?
#   TODO: Adjust "frames" for multiple step actions?

def request_handler(request):
    """
    Handles POST/GET requests for the poker game server. Assumes the POST/GET
    requests provide the following information:

    POST: user={user: str}&action={action: str}&amount={amount:str of int}
    GET: None
    
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
    #   Initialize the players_table and states_table SQL database
    # create_player_database(players_db)
    # create_state_database(state_db)
    conn_players = sqlite3.connect(players_db)
    c_player = conn_players.cursor()
    c_player.execute('''CREATE TABLE IF NOT EXISTS players_table 
                        (user text, bal int, bet int, invested int, 
                        cards text, position int);''')
    conn_state = sqlite3.connect(state_db)
    c_state = conn_state.cursor()
    c_state.execute('''CREATE TABLE IF NOT EXISTS states_table 
                        (deck text, board text, dealer int, action
                        int, pot int);''')

    game_state = ""
    if request['method'] == 'GET':
        user = request["values"]["user"]
        game_state = get_handler(user, request, c_player, c_state)
    elif request['method'] == 'POST':
        game_state = post_handler(request, c_player, c_state)

    #   TODO: Figure out if this is the right order of commit/close
    conn_players.commit()
    conn_players.close()
    conn_state.commit()
    conn_state.close()
    return game_state


def get_handler(user, request, players_cursor, states_cursor):
    """
    Handles a GET request as defined in the request_handler function.
    Returns a string representing the game state as defined in
    request_handler.

    Args:
        request (dict): maps request params to corresponding values
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table

    Returns:
        TODO: A JSON string representing the players and state of 
        the game as defined above

        Currently returns the game state as specified by the
        display_game function
    """
    
    users_query = '''SELECT * FROM players_table;'''
    users = players_cursor.execute(users_query).fetchall()
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()
    if users[0][USERNAME] == user and len(game_state) == 0:
      possible_actions = ["start"]
      
      return str(len(possible_actions)) + "$" + "@".join(possible_actions) + "@"
    else:
      game_action = game_state[ACTION]
      user_query = '''SELECT * FROM players_table WHERE user = ?;'''
      user_position = players_cursor.execute(user_query, (user,)).fetchall()[0][POSITION]
      if game_action == user_position:
        possible_actions = ["leave", "check", "call", "bet", "raise", "fold"]
        return str(len(possible_actions)) + "$" + "@".join(possible_actions) + "@"
      else:
        possible_actions = ["leave"]
        return str(len(possible_actions)) + "$" + "@".join(possible_actions) + "@"      
 
      

    #return display_game(players_cursor, states_cursor)


def post_handler(request, players_cursor, states_cursor):
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

    return display_game(players_cursor, states_cursor)


def display_game(players_cursor, states_cursor):
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
    
    Returns:
        A string of the state of the game, formatted as described
        above
    """
    #   TODO: Return proper JSON message of the state of the game
    players_query = '''SELECT * FROM players_table;'''
    players = players_cursor.execute(players_query).fetchall()
    result = "players:\n"
    for p in players:
        result += str(p) + "\n"

    result += "\nstate:\n"
    current_state_query = '''SELECT * FROM states_table;'''
    state = states_cursor.execute(current_state_query).fetchall()
    for s in state:
        result += str(s) + "\n"
    
    return result


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
        start_new_hand(players_cursor, states_cursor, dealer)
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
        players_cursor (SQL Cursor) cursor for the players_table
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
        next_stage(players_cursor, states_cursor, 0)
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
                next_stage(players_cursor, states_cursor, len(board_cards))
                break
            elif i != 0:
                next_player = players[position]
                if next_player[CARDS] != '' and next_player[BALANCE] > 0:
                    update_action = ''' UPDATE states_table
                                        SET action = ? '''
                    states_cursor.execute(update_action, (position,))
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
    to_call = min(max_bet, player[BALANCE])  #  Min of bet and the user's chip stack
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
            break
    
    if not found:
        board_cards = game_state[BOARD].split(',')
        if len(board_cards) == 1:   #  empty case
            board_cards = []
        next_stage(players_cursor, states_cursor, len(board_cards))


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
        distribute_pots(players_cursor, states_cursor)
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
                break

        if not found:
            board_cards = game_state[BOARD].split(',')
            if len(board_cards) == 1:   #  empty case
                board_cards = []
            next_stage(players_cursor, states_cursor, len(board_cards))


def start_new_hand(players_cursor, states_cursor, dealer_position):
    """
    Begins a new hand at the table. Posts blinds and deals two cards
    to each player. Updates player and game states.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        dealer_position (int): the dealer position ranging [0, # players)
    """
    #   Post blinds
    post_blinds(players_cursor, states_cursor, dealer_position)

    #   Deal cards
    deal_table(players_cursor, states_cursor)


def post_blinds(players_cursor, states_cursor, dealer_position):
    """
    Post blinds for the small blind and big blind positions.
    Assumes that there are at least three players. Updates the
    pot size and dealer position.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        dealer_position (int): the dealer position ranging [0, # players)
    """
    query = '''SELECT * FROM players_table;'''
    players = players_cursor.execute(query).fetchall()
    small = (dealer_position + 1) % len(players)
    big = (dealer_position + 2) % len(players)

    for seat in players:
        user = seat[USERNAME]
        bal = seat[BALANCE]
        position = seat[POSITION]
        #   Update player's balance and bet if they are small/big blind
        if position == small or position == big:
            blind = SMALL_BLIND if (position == small) else BIG_BLIND
            bet = blind if (bal >= blind) else bal
            bal = (bal - blind) if (bal >= blind) else 0
            invested = bet
            update_blinds = ''' UPDATE players_table
                                SET bal = ?,
                                    bet = ?,
                                    invested = ?
                                WHERE user = ?'''
            players_cursor.execute(update_blinds, (bal, bet, invested, user))
    
    #   Update the pot size, dealer position, who's action it is
    state_update = ''' UPDATE states_table
                       SET dealer = ? ,
                           pot = ?,
                           action = ?'''
    update_values = (dealer_position, SMALL_BLIND + BIG_BLIND, 
                    (dealer_position + 3) % len(players))
    states_cursor.execute(state_update, update_values)


def deal_table(players_cursor, states_cursor):
    """
    Deals two random cards to each player without replacement. 
    These two cards are updated in the players_table. The remaining 
    deck of cards is stored in state_table.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
    """
    deck = {c for c in cards}
    players = players_cursor.execute('''SELECT * FROM players_table''').fetchall()

    for seat in players:
        user = seat[USERNAME]
        #   Draw two cards, update the current deck, and update player
        two_cards = random.sample(deck, 2)
        deck.remove(two_cards[0])
        deck.remove(two_cards[1])
        hand = ",".join(two_cards)
        update_cards = ''' UPDATE players_table
                           SET cards = ?
                           WHERE user = ? '''
        players_cursor.execute(update_cards, (hand, user))

    #   Update the deck with remaining cards
    update_deck = ''' UPDATE states_table
                      SET deck = ? '''
    states_cursor.execute(update_deck, (",".join(deck),))

#   TODO: TEST THIS
def next_stage(players_cursor, states_cursor, num_board_cards):
    """
    Updates the game state by going into the next stage (e.g. Preflop to Flop,
    Flop to Turn, Turn to River, or River to Showdown). Collects all bets on
    previous street and updates the pot size.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        num_board_cards (int): 0, 3, 4, or 5 for the # of cards on the board
    """
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()[0]
    players_query = '''SELECT * FROM players_table ORDER BY position ASC;'''
    players = players_cursor.execute(players_query).fetchall()

    #   Remove all the bets 
    #   Note: we don't need to update the pot size b/c calling/betting/raising
    #   should automatically update the pot size as the action goes. Re-updating
    #   here will just double count the bets
    for user in players:
        update_bet = ''' UPDATE players_table
                            SET bet = ?
                            WHERE user = ?'''
        players_cursor.execute(update_bet, (0, user[USERNAME]))

    #   Update game state for the next street
    if num_board_cards == 5:  #  River
        distribute_pots(players_cursor, states_cursor)
    else:
        #   Draw the next card(s) for the board based on street
        to_deal = 3 if num_board_cards == 0 else 1
        deck = {c for c in game_state[DECK].split(',')}
        new_cards = random.sample(deck, to_deal)
        deck.difference_update(new_cards)

        #   Find the next action to go to
        #   This should be the first user with cards after the dealer
        next_action = 0
        for i in range(1, len(players) + 1):
            position = (game_state[DEALER] + i) % len(players)
            user = players[position]
            if user[CARDS] != '':  #  If the user has cards
                next_action = position
                break
        
        #   Update game state
        new_deck = ",".join(deck)
        comma = "," if to_deal != 3 else ""
        new_board = game_state[BOARD] + comma + ",".join(new_cards)
        update_cards = ''' UPDATE states_table
                           SET deck = ?,
                               board = ?,
                               action = ?'''
        states_cursor.execute(update_cards, (new_deck, new_board, next_action))


def distribute_pots(players_cursor, states_cursor):
    """
    Distribute all pots to the winners (this includes all side pots). Updates 
    the player state by removing bets and cards and updating the balance if 
    necessary. Updates the game state by removing the deck, board, and pot.
    Afterwards, start a new hand.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        winner (Array): list of winner names for each pot. The first winner 
            is for the main pot, the second winner is for the first side pot,
            the third winner is for the second side pot, etc. The size of
            the winner array must be equal to the size of the side pot 
            array + 1 (the main pot).
    """
    players_query = '''SELECT * FROM players_table ORDER BY position ASC;'''
    players = players_cursor.execute(players_query).fetchall()
    query = '''SELECT * FROM states_table;'''
    game_state = states_cursor.execute(query).fetchall()[0]
    
        #   Maps username to [chips invested, chips to add to bal, still live]
    all_playing = {p[USERNAME]: [p[INVESTED], 0, p[CARDS] != ''] for p in players if p[INVESTED] > 0}
    to_handle = [p for p in all_playing.keys()]
    while len(to_handle) > 1:
        min_stack = min([all_playing[k][0] for k in to_handle])
        pot = min_stack * len(to_handle)
        for p in to_handle:
            all_playing[p][0] -= min_stack
        
        player_card_list = [(p[USERNAME], p[CARDS].split(',')) for p in players 
                            if (p[USERNAME] in to_handle) and all_playing[p[USERNAME]][2]]
        board_cards = game_state[BOARD].split(',')
        winners = find_winners(player_card_list, board_cards)
        for p in winners:
            all_playing[p][1] += pot / len(winners)
        
        to_handle = [p for p, v in all_playing.items() if v[0] > 0]
    
    if len(to_handle) == 1:
        p = to_handle[0]
        all_playing[p][1] += all_playing[p][0]
        all_playing[p][0] = 0

    for player in players:
        name = player[USERNAME]
        delta = all_playing[name][1] if name in all_playing else 0
        new_bal = player[BALANCE] + delta
        new_bet = 0
        new_invested = 0
        update_user = ''' UPDATE players_table
                            SET bal = ?,
                                bet = ?,
                                invested = ?,
                                cards = ?
                            WHERE user = ?'''
        players_cursor.execute(update_user, (new_bal, new_bet, new_invested, '', player[USERNAME]))
    
    #   Update game state. Remove deck, board, and pot
    update_state = ''' UPDATE states_table
                        SET deck = ?,
                            board = ?,
                            pot = ? '''
    states_cursor.execute(update_state, ('', '', 0))

    #   Now start a new hand
    start_new_hand(players_cursor, states_cursor, (game_state[DEALER] + 1) % len(players))


def find_winners(players, board_cards):
    """
    players = (username, cards -> ['Ah', 'Kh'])
    board = ['Ah', ...]
    """
    #   TODO: fix magic #
    best_hand = 0
    best_hand_players = []
    for player in players:
        hole_cards = player[1]
        hand_rank, hand = find_best_hand(hole_cards, board_cards)

        if hand_rank > best_hand:
            best_hand = hand_rank
            best_hand_players = [(player[0], hand)]
        elif hand_rank == best_hand:
            best_hand_players.append((player[0], hand))
  
    winners = [best_hand_players[0][0]]
    if len(best_hand_players) > 1:
        #   Convert hand to list of numbers
        hands = [(k[0], [card_order_dict[j[0]] for j in k[1]]) for k in best_hand_players]
        hands.sort(key=lambda x: [x[1][0], x[1][1], x[1][2], x[1][3], x[1][4]], reverse=True)
        winners = [i[0] for i in hands if i[1] == hands[0][1]]
    return winners


def find_best_hand(hole_cards, board):
    cards = hole_cards + (board if len(board) == 5 else [])
    #   TODO: don't call funcitons twice? performance optimization?
    if check_straight_flush(cards)[0]:
        return (9, check_straight_flush(cards)[1])
    elif check_four_of_a_kind(cards)[0]:
        return (8, check_four_of_a_kind(cards)[1])
    elif check_full_house(cards)[0]:
        return (7, check_full_house(cards)[1])
    elif check_flush(cards)[0]:
        return (6, check_flush(cards)[1])
    elif check_straight(cards)[0]:
        return (5, check_straight(cards)[1])
    elif check_three_of_a_kind(cards)[0]:
        return (4, check_three_of_a_kind(cards)[1])
    elif check_two_pair(cards)[0]:
        return (3, check_two_pair(cards)[1])
    elif check_one_pair(cards)[0]:
        return (2, check_one_pair(cards)[1])
    return (1, check_high_card(cards)[1])


#   Functions to check if a certain type of hand exists
def check_straight_flush(hand):
    """
    Checks if the player's hand and board make a straight flush.
    IMPORTANT: Assumes that no better hand can be made.

    Args:
        hand (list of str): non-empty list of cards
            e.g. ['Ah', 'Ks', 'Qs', '3h', '4h', 'Js', 'Tc']
    
    Returns:
        A tuple of length 2 where the first entry is a boolean,
        indicating whether a straight flush is present, and the
        second entry is a list of str of the best straight flush
        hand made (if there is none, then there is no second entry).
        The hand is organized from most to least important card.
    """
    #   Not actually right, flush and straight can be different cards
    if check_flush(hand)[0] and check_straight(hand)[0]:
        return (True, check_flush(hand)[1])
    else:
        return (False,)


def check_four_of_a_kind(hand):
    """
    Checks if the player's hand and board make a four of a kind.
    IMPORTANT: Assumes that no better hand can be made.

    Args:
        hand (list of str): non-empty list of cards
    
    Returns:
        A tuple of length 2 where the first entry is a boolean,
        indicating whether a four of a kind is present, and the
        second entry is a list of str of the best four of a kind
        hand made (if there is none, then there is no second entry).
        The hand is organized from most to least important card.
    """
    cards_dict = count_cards(hand)
    
    if max(cards_dict.values()) == 4:
        mode = [k for k, v in cards_dict.items() if v == 4][0]
        remaining = [k for k, v in cards_dict.items() if v != 4]
        highest_card = sort_cards(remaining)[0]
        return (True, [mode]*4 + [highest_card])
    return (False,)


def check_full_house(hand):
    """
    Checks if the player's hand and board make a full house.
    IMPORTANT: Assumes that no better hand can be made.

    Args:
        hand (list of str): non-empty list of cards
    
    Returns:
        A tuple of length 2 where the first entry is a boolean,
        indicating whether a full house is present, and the
        second entry is a list of str of the best full house
        hand made (if there is none, then there is no second entry).
        The hand is organized from most to least important card.
    """
    if check_three_of_a_kind(hand)[0]:
        three_kind = check_three_of_a_kind(hand)[1][0]
        remaining = [k for k in hand if k[0] != three_kind]
        if check_one_pair(hand)[0]:
            pair = check_one_pair(remaining)[1][0]
            return (True, [three_kind]*3 + [pair]*2)
    return (False,)


def check_flush(hand):
    """
    Checks if the player's hand and board make a flush.
    IMPORTANT: Assumes that no better hand can be made.

    Args:
        hand (list of str): non-empty list of cards
    
    Returns:
        A tuple of length 2 where the first entry is a boolean,
        indicating whether a flush is present, and the
        second entry is a list of str of the best flush
        hand made (if there is none, then there is no second entry).
        The hand is organized from most to least important card.
    """
    suits = [i[1] for i in hand]
    suit_dict = {}
    for s in suits:
        if s in suit_dict:
            suit_dict[s] += 1
        else:
            suit_dict[s] = 1
    
    if max(suit_dict.values()) >= 5:
        max_suit = [k for k, v in suit_dict.items() if v == max(suit_dict.values())][0]
        suited_cards = [k for k in hand if k[1] == max_suit]
        highest_cards = sort_cards(suited_cards)[1]
        return (True, highest_cards[:5])
    return (False,)


def check_straight(hand):
    """
    Checks if the player's hand and board make a straight.
    IMPORTANT: Assumes that no better hand can be made.

    Args:
        hand (list of str): non-empty list of cards
    
    Returns:
        A tuple of length 2 where the first entry is a boolean,
        indicating whether a straight is present, and the
        second entry is a list of str of the best straight
        hand made (if there is none, then there is no second entry).
        The hand is organized from most to least important card.
    """
    return (False,)


def check_three_of_a_kind(hand):
    """
    Checks if the player's hand and board make a three of a kind.
    IMPORTANT: Assumes that no better hand can be made.

    Args:
        hand (list of str): non-empty list of cards
    
    Returns:
        A tuple of length 2 where the first entry is a boolean,
        indicating whether a three of a kind is present, and the
        second entry is a list of str of the best three of a kind
        hand made (if there is none, then there is no second entry).
        The hand is organized from most to least important card.
    """
    cards_dict = count_cards(hand)
    
    if max(cards_dict.values()) == 3:
        mode = [k for k, v in cards_dict.items() if v == 3][0]
        remaining = [k for k, v in cards_dict.items() if v != 3]
        remaining_sorted = sort_cards(remaining)
        return (True, [mode]*3 + remaining_sorted[:2])
    return (False,)


def check_two_pair(hand):
    """
    Checks if the player's hand and board make a two pair.
    IMPORTANT: Assumes that no better hand can be made.

    Args:
        hand (list of str): non-empty list of cards
    
    Returns:
        A tuple of length 2 where the first entry is a boolean,
        indicating whether a two pair is present, and the
        second entry is a list of str of the best two pair
        hand made (if there is none, then there is no second entry).
        The hand is organized from most to least important card.
    """
    cards_dict = count_cards(hand)
    pairs = [k for k, v in cards_dict.items() if v == 2]
    if len(pairs) >= 2:
        sorted_cards = sort_cards(pairs)
        first_pair = sorted_cards[0]
        second_pair = sorted_cards[2]
        remaining_cards = [k for k in hand if k != first_pair and k != second_pair]
        highest = sort_cards(remaining_cards)[0]
        return (True, [first_pair]*2 + [second_pair]*2 + [highest])
    return (False,)


def check_one_pair(hand):
    """
    Checks if the player's hand and board make a pair.
    IMPORTANT: Assumes that no better hand can be made.

    Args:
        hand (list of str): non-empty list of cards
    
    Returns:
        A tuple of length 2 where the first entry is a boolean,
        indicating whether a pair is present, and the
        second entry is a list of str of the best pair
        hand made (if there is none, then there is no second entry).
        The hand is organized from most to least important card.
    """
    cards_dict = count_cards(hand)
    pairs = [k for k, v in cards_dict.items() if v == 2]
    if len(pairs) == 1:
        highest_pair_card = sort_cards(pairs)[0]
        remaining_cards = [k for k, v in cards_dict.items() if k != highest_pair_card]
        sort_remaining = sort_cards(remaining_cards)
        return (True, [highest_pair_card]*2 + sort_remaining[:3])
    return (False,)


def check_high_card(hand):
    """
    Returns the hand with high card. IMPORTANT: Assumes that no 
    better hand can be made.

    Args:
        hand (list of str): non-empty list of cards
    
    Returns:
        A tuple of length 2 where the first entry is true (since
        high card is the worst possible poker hand), and the
        second entry is a list of str of the best high card
        hand made. The hand is organized from most to least 
        important card.
    """
    return (True, sort_cards(hand)[:5])


def sort_cards(cards):
    """
    Sorts the cards from highest to lowest.

    Args:
        cards (list of str): non-empty list of cards
    
    Returns:
        a non-empty list of cards from highest to lowest ranking.
    """
    ranked_cards = [(k, card_order_dict[k[0]]) for k in cards]
    ranked_cards.sort(key=lambda x: x[1], reverse=True)
    return [k[0] for k in ranked_cards]


def count_cards(cards):
    """
    Counts the cards
    """
    #   TODO: default dict?
    cards_dict = {}
    for card in cards:
        if card[0] in cards_dict:
            cards_dict[card[0]] += 1
        else:
            cards_dict[card[0]] = 1
    return cards_dict


# if __name__ == "__main__":
    #   Side pot tests

    #   Even split
    # players = [('kev2010', 650, 0, 300, '2d,2c', 0),
    #             ('jasonllu', 1350, 0, 300, '3c,Qc', 1),
    #             ('baptiste', 725, 0, 300, 'Kd,7s', 2)]
    # game_state = ('','Ac,Ah,Ad,Ah,Ks', 2, 0, 0)

    #   Two winners, one loser
    # players = [('kev2010', 650, 0, 300, '2d,2c', 0),
    #             ('jasonllu', 1350, 0, 300, 'Kc,Qc', 1),
    #             ('baptiste', 725, 0, 300, 'Kd,7s', 2)]
    # game_state = ('','Ac,Ah,Ad,Jh,Ks', 2, 0, 0)

    #   One winner, two losers
    # players = [('kev2010', 650, 0, 300, 'Ad,2c', 0),
    #             ('jasonllu', 1350, 0, 300, 'Jc,Tc', 1),
    #             ('baptiste', 725, 0, 300, '2d,3s', 2)]
    # game_state = ('','Ac,Th,Ad,Jh,Ks', 2, 0, 0)

    #   1 main pot, 1 side pot (smallest stack wins)
    # players = [('kev2010', 0, 0, 150, 'Ad,2c', 0),
    #             ('jasonllu', 1350, 0, 300, 'Jc,Tc', 1),
    #             ('baptiste', 725, 0, 300, '2d,3s', 2)]
    # game_state = ('','Ac,Th,Ad,Jh,Ks', 2, 0, 0)

    #   1 main pot, 1 side pot (smallest then middle stack wins)
    # players = [('kev2010', 0, 0, 150, 'Ad,2c', 0),
    #             ('jasonllu', 1350, 0, 300, 'Jc,Tc', 1),
    #             ('baptiste', 725, 0, 600, '2d,3s', 2)]
    # game_state = ('','Ac,Th,Ad,Jh,Ks', 2, 0, 0)

    #   Folding
    # players = [('kev2010', 950, 50, 50, '2h,Ks', 0),
    #             ('jasonllu', 975, 0, 0, '', 1),
    #             ('baptiste', 975, 25, 25, '', 2)]
    # game_state = ('','', 2, 0, 0)

    # #   Maps username to [chips invested, chips to add to bal, still live]
    # all_playing = {p[USERNAME]: [p[INVESTED], 0, p[CARDS] != ''] for p in players if p[INVESTED] > 0}
    # to_handle = [p for p in all_playing.keys()]
    # while len(to_handle) > 1:
    #     min_stack = min([all_playing[k][0] for k in to_handle])
    #     pot = min_stack * len(to_handle)
    #     for p in to_handle:
    #         all_playing[p][0] -= min_stack
        
    #     player_card_list = [(p[USERNAME], p[CARDS].split(',')) for p in players 
    #                         if (p[USERNAME] in to_handle) and all_playing[p[USERNAME]][2]]
    #     board_cards = game_state[BOARD].split(',')
    #     winners = find_winners(player_card_list, board_cards)
    #     for p in winners:
    #         all_playing[p][1] += pot / len(winners)
        
    #     to_handle = [p for p, v in all_playing.items() if v[0] > 0]
    
    # if len(to_handle) == 1:
    #     p = to_handle[0]
    #     all_playing[p][1] += all_playing[p][0]
    #     all_playing[p][0] = 0
    
    # print(all_playing)
