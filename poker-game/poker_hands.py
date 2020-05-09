"""Finds the best poker hand that can be made.

This module abstracts the process of finding the best poker hand that
can be made given a set of hole cards and board cards.

Attributes:
    card_order_dict (dict: str -> int): maps card values to their
        numerical ranking
"""

card_order_dict = {"2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, 
                   "T":10, "J":11, "Q":12, "K":13, "A":14}
                   
def find_best_hand(hole_cards, board):
    """
    Given two hole cards and five board cards, finds the best
    poker hand that can be made from any combination of five
    cards from that set.

    Args:
        hole_cards (list of str): a length two list of two
            cards
        board (list of str): a length five list of five
            cards
    
    Returns:
        A tuple where the first elt is a numerical ranking
        of the hand (1 to 9, where 9 is a straight flush,
        the highest), and the second elt is a list of str
        of the five cards that make the best hand.
    """
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
    if check_flush(hand)[0]:
        highest_flush = check_flush(hand)[1]
        suit = highest_flush[0][1]
        cards_with_suit = [c for c in hand if c[1] == suit]
        if check_straight(cards_with_suit)[0]:
            return (True, check_straight(cards_with_suit)[1])
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
        #   Find biggest 3 of a kind
        cards_dict = count_cards(hand)
        three_peats = [k for k, v in cards_dict.items() if v == 3]
        three_kind_val = 0
        three_kind = ''
        for three in three_peats:
            if card_order_dict[three] > three_kind_val:
                three_kind_val = card_order_dict[three]
                three_kind = three

        remaining = [k for k in hand if k[0] != three_kind]
        if check_one_pair(remaining)[0]:
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
        highest_cards = sort_cards(suited_cards)
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
    cards_dict = count_cards(hand)
    ranks_sorted = sort_cards(cards_dict.keys())  #  Gets rid of suits

    #   Keep track of a counter to count consecutive ranks
    counter = 0
    prev_rank = 0
    prev_cards = []
    for rank in ranks_sorted:  #  ranks_sorted goes from high to low
        rank_int = card_order_dict[rank]
        if prev_rank - rank_int == 1:
            counter += 1
            prev_cards.append(rank)
        else:
            counter = 1
            prev_cards = [rank]
        prev_rank = rank_int
        if counter == 5:
            return (True, prev_cards)

    #   Check special case of A to 5 straight
    low_straight = ['5', '4', '3', '2']
    if ranks_sorted[-4:] == low_straight and 'A' in cards_dict.keys():
        return (True, low_straight + ['A'])

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
        second_pair = sorted_cards[1]
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
    pairs = [k for k, v in cards_dict.items() if v >= 2]
    if len(pairs) >= 1:
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
    Sorts the cards from highest to lowest rank.

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
    Counts the # of appearances of each card rank.

    Args:
        cards (list of str): a list of card ranks
    
    Returns:
        A dictionary mapping card ranks to the # of times it
        appears in the "cards" list.
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
    # #   Straight tests
    # #   A to T
    # hand1 = ["Ah", "Kd", "Td", "4s", "3d", "Qd", "Jh"]

    # #   9 to 5
    # hand2 = ["5h", "4d", "6d", "7s", "9d", "Qd", "8h"]

    # #   A to 5
    # hand3 = ["5h", "4d", "2d", "3s", "9d", "Qd", "Ah"]

    # #   No straight
    # hand4 = ["3h", "4d", "6d", "7s", "9d", "Qd", "8h"]

    # print(check_straight(hand4))

    # #   Flush tests
    # #   K high d
    # hand1 = ["Ah", "Kd", "Td", "4s", "3d", "Qd", "Jd"]

    # #   A high h
    # hand2 = ["Ah", "3d", "Th", "4h", "3h", "Qd", "Jh"]

    # #   7 high h
    # hand3 = ["2h", "3d", "7h", "4h", "3h", "Qd", "6h"]

    # #   more than 5 spades, Q high s
    # hand4 = ["7s", "3s", "Ah", "4s", "Js", "Qs", "6s"]

    # #   no flush
    # hand5 = ["3h", "4d", "6d", "7s", "9d", "Qd", "8h"]

    # print(check_flush(hand1))

    # # Full house tests
    # #   Kings over 3
    # hand1 = ["Kh", "Kd", "Td", "3s", "3d", "Qd", "Ks"]

    # #   4s over Ts
    # hand2 = ["Th", "4c", "Tc", "4h", "Ks", "Qd", "4h"]

    # #   8s over 6s (3 6s and 3 8s)
    # hand3 = ["6h", "8d", "6s", "8c", "8h", "Qd", "6c"]

    # #   9s over 7s (with 2 6s)
    # hand4 = ["9s", "6s", "6h", "9d", "7s", "7c", "9c"]

    # #   A over 6s (with 3 K)
    # hand5 = ["Kh", "Kd", "Kc", "As", "Ad", "Qd", "Ah"]

    # #   3 of a kind, no full house
    # hand6 = ["Kh", "Kd", "Td", "3s", "7d", "Qd", "Ks"]

    # #   3 pairs, no full house
    # hand7 = ["Kh", "Kd", "Td", "3s", "3d", "Qd", "Ts"]

    # print(check_full_house(hand1))

    # #   4 of a kind tests
    # #   4 K
    # hand1 = ["Kh", "Kd", "Td", "3s", "3d", "Kc", "Ks"]

    # #   4 4
    # hand2 = ["4h", "4c", "Tc", "4s", "Ks", "Qd", "4d"]

    # #   4 3, 3 6
    # hand3 = ["3s", "3c", "6c", "6h", "6s", "3d", "3h"]

    # #   3 pairs, no 4 of a kind
    # hand4 = ["Kh", "Kd", "Td", "3s", "3d", "Qd", "Ts"]

    # #   2 3 of a kind
    # hand5 = ["Kh", "Ks", "Td", "3h", "3d", "Kd", "3s"]

    # print(check_four_of_a_kind(hand5))

    # #   Straight flush tests
    # #   royal
    # hand1 = ["Ad", "Kd", "Td", "4s", "3d", "Qd", "Jd"]

    # #   T high
    # hand2 = ["9h", "3d", "Th", "4s", "6h", "7h", "8h"]

    # #   Q straight flush with an A high flush
    # hand3 = ["Ts", "9s", "As", "4c", "Js", "Qs", "8s"]

    # #   K straight flush with an A high straight
    # hand4 = ["Jh", "9h", "Th", "As", "9d", "Qh", "Kh"]

    # #   straight + flush present, but no straight flush
    # hand5 = ["2h", "3d", "6h", "4h", "5h", "Qd", "Kh"]

    # print(check_straight_flush(hand5))