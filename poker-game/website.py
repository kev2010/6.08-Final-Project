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

    ret = ret.split("(")

    #   TODO: Figure out if this is the right order of commit/close
    conn_players.close()
    conn_state.close()

    x = "<h1> WELCOME TO POKER! </h1> <br><br> <h2> by team079 </h2> <br><br> A game is in progress... <br><br>"

    x += '''
              <tr>
            <th>Name</th>
            <th>Balance</th> 
            <th>Bet</th>
          </tr>
    
    '''
    x += '''
        <table style="width:100%">'''
    for i in range(1,4):
        sp = ret[i].split(",")
        x += '''<tr>
        <th> <strong>'''+sp[0] + '''</strong> </th>
        <th>''' + sp[1] + '''</th>
        <th>''' + sp[2] + '''</th>
        </tr>'''

    x+= "</table>"

    x+= "<br><br><br> copyright team079!"

    return x
    
