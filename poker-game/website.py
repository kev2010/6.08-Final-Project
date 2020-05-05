import sqlite3
import random
import sys
sys.path.append('__HOME__/team079/poker-game')
from poker_actions import *
from room_actions import *
from render_game import *

players_db = '__HOME__/team079/poker-game/players.db'
state_db = '__HOME__/team079/poker-game/state.db'


def request_handler(request):
    """
    insert cool spec here
    """

    conn_players = sqlite3.connect(players_db)
    conn_state = sqlite3.connect(state_db)
    c_state = conn_state.cursor()
    c_player = conn_players.cursor()

    ret = None
    if request['method'] == 'GET':
        user = request["values"]["user"]
        ret = display_game(c_player, c_state, user)


    #   TODO: Figure out if this is the right order of commit/close
    conn_players.close()
    conn_state.close()
    return ret