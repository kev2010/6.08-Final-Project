"""Contains settings for the poker game.

This module contains global variables used throughout the Poker API.
"""
#   SQL db locations on server
players_db = '__HOME__/team079/poker-game/players.db'
state_db = '__HOME__/team079/poker-game/state.db'
frames_db = '__HOME__/team079/poker-game/frames.db'

#   Constants
MAX_PLAYERS = 3
SMALL_BLIND = 25
BIG_BLIND = 50
STARTING_STACK = 1000
all_ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
all_suits = ['s', 'c', 'd', 'h']
cards = {rank + suit for rank in all_ranks for suit in all_suits}

#   Global Frames
FRAMES = []

#   Player SQL DB indicies
USERNAME = 0
BALANCE = 1
BET = 2
INVESTED = 3
CARDS = 4
POSITION = 5
PLAYER_ID = 6

#   Game State SQL DB indicies
DECK = 0
BOARD = 1
DEALER = 2
ACTION = 3
POT = 4
STATE_ID = 5

#   Frames SQL DB indicies
STATE = 0
TIME = 1
FRAME_ID = 2
