import sqlite3
import random
# from databaseFuncs import *
players_db = '__HOME__/team079/poker-game/players.db'
state_db = '__HOME__/team079/poker-game/state.db'

MAX_PLAYERS = 3
SMALL_BLIND = 25
BIG_BLIND = 50
STARTING_STACK = 1000
all_ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
all_suits = ['s', 'c', 'd', 'h']
cards = {rank + suit for rank in all_ranks for suit in all_suits}


#   TODO: Make these functions take in database name string parameters


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
                        (user text, bal int, bet int, cards text, 
                        position int);''')
    conn_state = sqlite3.connect(state_db)
    c_state = conn_state.cursor()
    c_state.execute('''CREATE TABLE IF NOT EXISTS states_table 
                        (deck text, board text, dealer int, action
                        int, pot int);''')

    game_state = ""
    if request['method'] == 'GET':
        game_state = get_handler(request, c_player, c_state)
    elif request['method'] == 'POST':
        game_state = post_handler(request, c_player, c_state)

    #   TODO: Figure out if this is the right order of commit/close
    conn_players.commit()
    conn_players.close()
    conn_state.commit()
    conn_state.close()
    return game_state


def get_handler(request, players_cursor, states_cursor):
    """
    Handles a GET request as defined in the request_handler function.
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
    return ""


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
    amount = request['form']['amount']

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
        raise ValueError
    elif action == "raise":
        raise ValueError
    elif action == "fold":
        raise ValueError
    else:
        return "Requested action not recognized!"

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
    insert_player = '''INSERT into players_table VALUES (?,?,?,?,?);'''
    players_cursor.execute(insert_player,
                           (user, STARTING_STACK, 0, "", len(players)))


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
    if users[0][0] == user:
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

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Raises:
        ValueError: if action is not on the user or checking is illegal
    """
    #   Make sure action is on the user
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()[0]
    game_action = game_state[3]
    user_query = '''SELECT * FROM players_table WHERE user = ?;'''
    user_position = players_cursor.execute(user_query, (user,)).fetchall()[0][4]
    if game_action != user_position:
        raise ValueError

    #   Make sure checking is a legal option
    #   Checking is legal only if there are no bets yet
    bets_query = '''SELECT * FROM players_table WHERE bet > ?'''
    bets = states_cursor.execute(bets_query, (0,)).fetchall()
    if bets:
        raise ValueError

    #   Otherwise, we pass the action to the next player
    #   that has cards, or end the action
    pass_action(players_cursor, states_cursor, user_position)

#   TODO: TEST THIS
def call(players_cursor, states_cursor, user):
    """
    Handles a poker call request. Calls the previous bet and passes
    the turn to the next player or goes to the next stage if calling
    is a legal action. Assumes the board has either 0, 3, 4, or 5 cards.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): non-empty username
    
    Raises:
        ValueError: if action is not on the user or calling is illegal 
    """
    #   Make sure action is on the user
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()[0]
    game_action = game_state[3]
    user_query = '''SELECT * FROM players_table WHERE user = ?;'''
    user_position = players_cursor.execute(user_query, (user,)).fetchall()[0][4]
    if game_action != user_position:
        print(game_action)
        print(type(game_action))
        print(user_position)
        print(type(user_position))
        raise ValueError

    #   Make sure calling is a legal option
    #   Calling is legal only if there are bets present
    bets_query = '''SELECT * FROM players_table WHERE bet > ?'''
    bets = states_cursor.execute(bets_query, (0,)).fetchall()
    if len(bets) == 0:
        raise ValueError
    
    #   Find the max bet that user has to call
    max_bet = 0
    for better in bets:
        if better[2] > max_bet:
            max_bet = better[2]
    to_call = min(max_bet, user[1])  #  Min of bet and the user's chip stack
    #   Put the bet in front of the user
    new_bet = to_call
    new_bal = user[1] + user[2] - to_call
    update_blinds = ''' UPDATE players_table
                        SET bal = ? ,
                            bet = ?
                        WHERE user = ?'''
    players_cursor.execute(update_blinds, (new_bal, new_bet, user))
    #   Update action
    pass_action(players_cursor, states_cursor, user_position)


def start_new_hand(players_cursor, states_cursor, dealer_position):
    """
    Begins a new hand at the table. Posts blinds and deals two cards
    to each player. Updates player and game states.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
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
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        dealer_position (int): the dealer position ranging [0, # players)
    """
    query = '''SELECT * FROM players_table;'''
    players = players_cursor.execute(query).fetchall()
    small = (dealer_position + 1) % len(players)
    big = (dealer_position + 2) % len(players)

    for seat in players:
        user = seat[0]
        bal = seat[1]
        position = seat[4]
        #   Update player's balance and bet if they are small/big blind
        if position == small or position == big:
            blind = SMALL_BLIND if (position == small) else BIG_BLIND
            bet = blind if (bal >= blind) else bal
            bal = (bal - blind) if (bal >= blind) else 0
            update_blinds = ''' UPDATE players_table
                                SET bal = ? ,
                                    bet = ?
                                WHERE user = ?'''
            players_cursor.execute(update_blinds, (bal, bet, user))
    
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
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
    """
    deck = {c for c in cards}
    players = players_cursor.execute('''SELECT * FROM players_table''').fetchall()

    for seat in players:
        user = seat[0]
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
def pass_action(players_cursor, states_cursor, user_position):
    """
    Passes the action to the next player in the round, if any. 
    Otherwise, goes to the next stage of the game.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user_position (int): the user's position ranging [0, # players)
    """
    players_query = '''SELECT * FROM players_table ORDER BY position ASC;'''
    players = players_cursor.execute(players_query).fetchall()
    query = '''SELECT * FROM states_table;'''
    game_state  = states_cursor.execute(query).fetchall()[0]
    for i in range(len(players)):
        position = (user_position + i) % len(players)
        #   If this user is the dealer, then the original user has ended the action
        if position == game_state[2]:
            board_cards = game_state[1].split(',')
            next_stage(players_cursor, states_cursor, len(board_cards))
        else:
            user = players[position]
            if user[3] != '':  #  If the user has cards
                update_action = ''' UPDATE states_table
                                    SET action = ? '''
                states_cursor.execute(update_action, (position,))

#   TODO: TEST THIS
def next_stage(players_cursor, states_cursor, num_board_cards):
    """
    Updates the game state by going into the next stage (e.g. Preflop to Flop,
    Flop to Turn, Turn to River, or River to Showdown)

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        num_board_cards (int): 0, 3, 4, or 5 for the # of cards on the board
    """
    if num_board_cards == 5:  #  River
        showdown()
    else:
        query = '''SELECT * FROM states_table;'''
        game_state  = states_cursor.execute(query).fetchall()[0]
        players_query = '''SELECT * FROM players_table ORDER BY position ASC;'''
        players = players_cursor.execute(players_query).fetchall()

        #   Draw the next card(s) for the board based on street
        to_deal = 3 if num_board_cards == 0 else 1
        deck = {c for c in game_state[0].split(',')}
        new_cards = random.sample(deck, to_deal)
        deck.difference_update(new_cards)

        #   Find the next action to go to
        #   This should be the first user with cards after the dealer
        next_action = 0
        for i in range(1, len(players) + 1):
            position = (game_state[2] + i) % len(players)
            user = players[position]
            if user[3] != '':  #  If the user has cards
                next_action = position
                break
        
        #   Update game state
        new_board = game_state[1] + ",".join(new_cards)
        update_cards = ''' UPDATE states_table
                           SET deck = ?,
                               board = ?,
                               action = ?'''
        states_cursor.execute(update_cards, (deck, new_board, next_action))


def showdown():
    pass
