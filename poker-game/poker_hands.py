card_order_dict = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, 
                   "T":10, "J":11, "Q":12, "K":13, "A":14}
                   
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
