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
    GET:None
    
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
                    "pot": 225"
                }
            }

    The game_state provides a list of players with the corresponding
    information. Some fields in the player information are private,
    such as the cards if player object is not the user sending the
    post request. The game_state also contains the state with the board
    cards, the current dealer position, and the total pot size.
    
    :param request: (dict) maps request params to corresponding values
    :return: (str) a JSON string representing the players and state of 
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
                        (deck text, board text, dealer int, 
                        pot int);''')

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
    return ""


def post_handler(request, players_cursor, states_cursor):
    #   Get the user, action, and amount from the POST request
    user = request['form']['user']
    action = request['form']['action']
    amount = request['form']['amount']

    #   Split actions based on type of request
    #   TODO: implement other actions
    if action == "join":
        join_game(players_cursor, states_cursor, user)
    elif action == "start":
        #   Check if the user is the host, which is player 0
        user_query = '''SELECT * FROM players_table WHERE user = ?;'''
        user_position = players_cursor.execute(user_query, (user,)).fetchall()[0][4]
        if user_position == 0:
            start_game(players_cursor, states_cursor)
    elif action == "leave":
        raise ValueError
    elif action == "check":
        raise ValueError
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

    :param players_cursor: (SQL Cursor) cursor for the players_table
    :param states_cursor: (SQL Cursor) cursor for the states_table
    :param user: (str) non-empty username
    :raises:
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


def start_game(players_cursor, states_cursor):
    """
    Starts the game with at least two players.
    
    :param players_cursor: (SQL Cursor) cursor for the players_table
    :param states_cursor: (SQL Cursor) cursor for the states_table
    """
    dealer = random.randint(0, MAX_PLAYERS - 1)
    start_new_hand(players_cursor, states_cursor, dealer)


def start_new_hand(players_cursor, state_cursor, dealer_position):
    """
    Begins a new hand at the table. Posts blinds and deals two cards
    to each player. Updates player and game states.

    :param players_cursor: (SQL Cursor) cursor for the players_table
    :param state_cursor: (SQL Cursor) cursor for the states_table
    :param dealer_position: (int) the dealer position ranging [0, # players)
    """
    #   Post blinds
    post_blinds(players_cursor, dealer_position)

    #   Deal cards
    deal_table(players_cursor, state_cursor)


def post_blinds(players_cursor, dealer_position):
    """
    Post blinds for the small blind and big blind positions.
    Assumes that there are at least three players.

    :param players_cursor: (SQL Cursor) cursor for the players_table
    :param dealer_position: (int) the dealer position ranging [0, # players)
    """
    query = '''SELECT * FROM players_table;'''
    players = players_cursor.execute(query).fetchall()
    small = dealer_position + 1
    big = dealer_position + 2

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


def deal_table(players_cursor, state_cursor):
    """
    Deals two random cards to each player without replacement. 
    These two cards are updated in the players_table. The remaining deck of cards
    is stored in state_table.

    :param players_cursor: (SQL Cursor) cursor for the players_table
    :param state_cursor: (SQL Cursor) cursor for the states_table
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
    state_cursor.execute(update_deck, (",".join(deck),))


# if __name__ == "__main__":
#     deck = {c for c in cards}
#     for i in range(3):
#         two_cards = random.sample(deck, 2)
#         deck.remove(two_cards[0])
#         deck.remove(two_cards[1])
#         hand = ",".join(two_cards)
#         print(hand)
#     print(len(",".join(deck)))
    
