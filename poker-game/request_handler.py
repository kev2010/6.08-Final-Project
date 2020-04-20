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
    :return: (str) a JSON string representing the state of the game as
            defined in the request handler
    """
    # Request Dictionary: {'method': 'GET', 'values': {}, 'args': []}
    # create_player_database(players_db)
    # create_state_database(state_db)

    if request['method'] == 'GET':
        return ""
    elif request['method'] == 'POST':
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


        user = request['form']['user']
        action = request['form']['action']
        amount = request['form']['amount']

        #   Split actions based on type of request
        #   TODO: implement other actions
        if action == "join":
            join_game(c_player, c_state, user)
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
        players = c_player.execute(players_query).fetchall()
        result = "players:\n"
        for p in players:
            result += str(p) + "\n"
        result += "\nstate:\n"
        current_state_query = '''SELECT * FROM states_table;'''
        state = c_state.execute(current_state_query).fetchall()
        for s in state:
            result += str(s) + "\n"

        #   TODO: Figure out if this is the right order of commit/close
        conn_players.commit()
        conn_players.close()
        conn_state.commit()
        conn_state.close()
        return result


def join_game(players_cursor, states_cursor, user):
    """
    Handles a join game request. Adds the user to the game if it
    is not full. Otherwise, rejects the user from joining. If the game
    becomes full, then start the game.

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
        #   TODO: Return proper message for joining full game
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

    #   If new player makes the game full, begin game with random dealer
    if len(players) == MAX_PLAYERS - 1:
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
    
