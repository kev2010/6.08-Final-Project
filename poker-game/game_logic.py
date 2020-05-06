import sys
import random
sys.path.append('__HOME__/team079/poker-game')
from settings import *
from render_game import *
from poker_hands import *

def start_new_hand(players_cursor, states_cursor, dealer_position, user):
    """
    Begins a new hand at the table. Posts blinds and deals two cards
    to each player. Updates player and game states.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        dealer_position (int): the dealer position ranging [0, # players)
        user (str): the user who sent the request
    """
    #   Post blinds
    post_blinds(players_cursor, states_cursor, dealer_position, user)

    #   Deal cards
    deal_table(players_cursor, states_cursor, user)


def post_blinds(players_cursor, states_cursor, dealer_position, user):
    """
    Post blinds for the small blind and big blind positions.
    Assumes that there are at least three players. Updates the
    pot size and dealer position.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        dealer_position (int): the dealer position ranging [0, # players)
        user (str): the user who sent the request
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

    FRAMES.append(display_game(players_cursor, states_cursor, user))


def deal_table(players_cursor, states_cursor, user):
    """
    Deals two random cards to each player without replacement. 
    These two cards are updated in the players_table. The remaining 
    deck of cards is stored in state_table.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): user who sent the request
    """
    deck = {c for c in cards}
    players = players_cursor.execute('''SELECT * FROM players_table''').fetchall()

    for seat in players:
        name = seat[USERNAME]
        #   Draw two cards, update the current deck, and update player
        two_cards = random.sample(deck, 2)
        deck.remove(two_cards[0])
        deck.remove(two_cards[1])
        hand = ",".join(two_cards)
        update_cards = ''' UPDATE players_table
                           SET cards = ?
                           WHERE user = ? '''
        players_cursor.execute(update_cards, (hand, name))

    #   Update the deck with remaining cards
    update_deck = ''' UPDATE states_table
                      SET deck = ? '''
    states_cursor.execute(update_deck, (",".join(deck),))

    FRAMES.append(display_game(players_cursor, states_cursor, user))

#   TODO: TEST THIS
def next_stage(players_cursor, states_cursor, num_board_cards, user):
    """
    Updates the game state by going into the next stage (e.g. Preflop to Flop,
    Flop to Turn, Turn to River, or River to Showdown). Collects all bets on
    previous street and updates the pot size.

    Args:
        players_cursor (SQL Cursor): cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        num_board_cards (int): 0, 3, 4, or 5 for the # of cards on the board
        user (str): user who sent the request
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
        FRAMES.append(display_game(players_cursor, states_cursor, user))
        distribute_pots(players_cursor, states_cursor, user)
    else:
        #   Draw the next card(s) for the board based on street
        to_deal = 3 if num_board_cards == 0 else 1
        deck = {c for c in game_state[DECK].split(',')}
        new_cards = random.sample(deck, to_deal)
        deck.difference_update(new_cards)

        #   Find the next action to go to
        #   This should be the first user with cards after the dealer
        next_action = 0
        found = False
        for i in range(1, len(players) + 1):
            position = (game_state[DEALER] + i) % len(players)
            user = players[position]
            if user[CARDS] != '' and user[BALANCE] > 0:  #  If the user has cards
                next_action = position
                found = True
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
        FRAMES.append(display_game(players_cursor, states_cursor, user))

        #   Everyone is all-in case
        if not found:
            next_stage(players_cursor, states_cursor, len(new_board.split(',')), user)


def distribute_pots(players_cursor, states_cursor, user):
    """
    Distribute all pots to the winners (this includes all side pots). Updates 
    the player state by removing bets and cards and updating the balance if 
    necessary. Updates the game state by removing the deck, board, and pot.
    Afterwards, start a new hand.

    Args:
        players_cursor (SQL Cursor) cursor for the players_table
        states_cursor (SQL Cursor): cursor for the states_table
        user (str): the user who sent the request
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

    FRAMES.append(display_game(players_cursor, states_cursor, user))

    #   Now start a new hand
    start_new_hand(players_cursor, states_cursor, (game_state[DEALER] + 1) % len(players), user)


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

    #   all-in and split
    # players = [('kev2010', 25, 0, 975, '2h,Ks', 0),
    #             ('jasonllu', 0, 0, 975, '2s,Kh', 1),
    #             ('baptiste', 975, 0, 25, '', 2)]
    # game_state = ('','Ah,Qh,Js,3c,4c', 2, 0, 0)

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
    #     print(winners)
    #     for p in winners:
    #         all_playing[p][1] += pot / len(winners)
        
    #     to_handle = [p for p, v in all_playing.items() if v[0] > 0]
    
    # if len(to_handle) == 1:
    #     p = to_handle[0]
    #     all_playing[p][1] += all_playing[p][0]
    #     all_playing[p][0] = 0
    
    # print(all_playing)