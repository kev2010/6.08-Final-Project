import sqlite3
import random
import sys
sys.path.append('__HOME__/team079/poker-game')
from poker_actions import *
from room_actions import *
from render_game import *

players_db = '__HOME__/team079/poker-game/players.db'
state_db = '__HOME__/team079/poker-game/state.db'

#   Delete?
def request_handler(request):
    """
    insert cool spec here
    """
    conn_players = sqlite3.connect(players_db)
    conn_state = sqlite3.connect(state_db)
    c_state = conn_state.cursor()
    c_player = conn_players.cursor()

    # ret = None
    # if request['method'] == 'GET':
    #     user = request["values"]["user"]
    #     ret = display_game(c_player, c_state, user)

    # ret = ret.split("(")

    # #   TODO: Figure out if this is the right order of commit/close
    # conn_players.close()
    # conn_state.close()

    # x = "<h1> WELCOME TO POKER! </h1> <br><br> <h2> by team079 </h2> <br><br> A game is in progress... <br><br>"

    # x += '''
    #     <table style="width:100%">'''

    # x += '''
    #           <tr>
    #         <th>Name</th>
    #         <th>Balance</th> 
    #         <th>Bet</th>
    #         <th> Cards </th>
    #       </tr>
    
    # '''

    # for i in range(1,4):
    #     sp = ret[i].split(",")
    #     x += '''<tr>
    #     <th>'''+sp[0] + '''</th>
    #     <th>''' + sp[1] + '''</th>
    #     <th>''' + sp[2] + '''</th>'''

    #     if user == sp[0]:
    #         x += '''<th>''' + sp[3] + " " + sp[4] + '''<th>'''
    #     else:
    #         x += '''<th> ** ** <th>'''
    #     x += '''</tr>'''

    # x+= "</table>"

    # x+= "<br><br><br> copyright team079!"

    # return x
    # return "<meta http-equiv=\"refresh\" content=\"3\" ><h1> HI </h1>"
    return '''
            <head>
                <title>Poker!</title>
                <style>
                    .main {
                        width: 1000px;
                    }

                    .table {
                        background-color: green;
                        height: 500px;
                        width: 80%;
                        border-radius: 50%;
                        margin: 0 auto;
                        border: 1em solid black;
                    }

                    .board {
                        position: relative;
                        top: 40%;
                        left: 30%;
                    }

                    .card-small {
                        border: .2em solid black;
                        border-radius: 10%;
                        height: 80px;
                        width: 56px; /*70% of height*/
                        margin-right: 5px;
                        float: left;
                        background-color: white;
                    }

                    .card-text {
                        margin: 0;
                        margin-top: 15%;
                        text-align: center;
                        font-size: 1.5em;
                        font-weight: bold;
                        padding: 0;
                    }

                    .card-img {
                        text-align: center;
                        margin: 0;
                        font-size: 2em;
                    }

                    .red {
                        color: red;
                    }

                    .black {
                        color: black;
                    }

                </style>
            </head>

            <body>
                <div class="main">
                    <h1> Welcome to Poker :) </h1>
                    <div class="table">
                        <div class="board">
                            <div class="card-small" id="flop1">
                                <p class="card-text black" id="flop1-rank">A</p>
                                <p class="card-img black" id="flop1-suit">&clubs;</p>
                            </div>
                            <div class="card-small" id="flop2">
                                <p class="card-text black" id="flop2-rank">10</p>
                                <p class="card-img black" id="flop2-suit">&spades;</p>
                            </div>
                            <div class="card-small" id="flop3">
                                <p class="card-text red" id="flop3-rank">K</p>
                                <p class="card-img red" id="flop3-suit">&hearts;</p>
                            </div>
                            <div class="card-small" id="turn">
                                <p class="card-text red" id="turn-rank">Q</p>
                                <p class="card-img red" id="turn-suit">&diams;</p>
                            </div>
                            <div class="card-small" id="river">
                                <p class="card-text red" id="river-rank">2</p>
                                <p class="card-img red" id="river-suit">&diams;</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="instructor-answer"></div>
            </body>

            <script>
                function display() {
                    let xhttp = new XMLHttpRequest();
                    var params = "type=spectate";
                    let url = "http://608dev-2.net/sandbox/sc/team079/team079/poker-game/request_handler.py";
                    
                    xhttp.onreadystatechange = function() {
                        if (this.readyState == 4 && this.status == 200) {
                            // XMLHttp will provide the servers response as text,s we need to parse to turn it into JSON
                            let response = JSON.parse(this.response); // 89

                            // Press f12 to see the console.log and see the full response body from the poker api
                            console.log(response);
                            let to_display = JSON.stringify(response);

                            if (response.state.length != 0){
                                gameState = response.state[0];

                                //  If there is a game going on
                                if (gameState.length != 0) {
                                    let board = gameState.board.split(",");

                                    // FLOP
                                    var showFlop = false;
                                    if (board.length === 3) {
                                        showFlop = true;
                                    }

                                    var flop1 = document.getElementById("flop1");
                                    var flop1rank = document.getElementById("flop1-rank");
                                    var flop1suit = document.getElementById("flop1-suit");
                                    flop1.hidden = !showFlop;
                                    if (showFlop) {
                                        flop1rank.innerHTML = board[0][0];
                                        //flop1suit.innerHTML = board[0][1];
                                    }

                                    let flop2 = document.getElementById("flop2");
                                    let flop2rank = document.getElementById("flop2-rank");
                                    let flop2suit = document.getElementById("flop2-suit");
                                    flop2.hidden = !showFlop;
                                    if (showFlop) {
                                        flop2rank.innerHTML = board[1][0];
                                        //flop2suit.innerHTML = board[1][1];
                                    }

                                    let flop3 = document.getElementById("flop3");
                                    let flop3rank = document.getElementById("flop3-rank");
                                    let flop3suit = document.getElementById("flop3-suit");
                                    flop3.hidden = !showFlop;
                                    if (showFlop) {
                                        flop3rank.innerHTML = board[2][0];
                                        //flop3suit.innerHTML = board[2][1];
                                    }

                                    // TURN
                                    var showTurn = false;
                                    if (board.length === 4) {
                                        showTurn = true;
                                    }

                                    let turn = document.getElementById("turn");
                                    let turnRank = document.getElementById("turn-rank");
                                    let turnSuit = document.getElementById("turn-suit");
                                    turn.hidden = !showTurn;
                                    if (showTurn) {
                                        turnRank.innerHTML = board[3][0];
                                        //turnSuit.innerHTML = board[3][1];
                                    }

                                    // RIVER
                                    var showRiver = false;
                                    if (board.length === 5) {
                                        showRiver = true;
                                    }

                                    let river = document.getElementById("river");
                                    let riverRank = document.getElementById("river-rank");
                                    let riverSuit = document.getElementById("river-suit");
                                    river.hidden = !showRiver;
                                    if (showRiver) {
                                        riverRank.innerHTML = board[4][0];
                                        //riverSuit.innerHTML = board[4][1];
                                    }
                                }
                            }
                            // Now, target the DIV in question, and set the innerHTML to the response
                            let targetDiv = document.getElementById("instructor-answer");
                            targetDiv.innerHTML = to_display;
                        }
                    }

                    xhttp.open("GET", url+"?"+params, true);
                    xhttp.send(null);
                }

                window.onload = display;

                setInterval(function(){
                    console.log("refreshing");
                    display();
                },1000);
            </script>
        '''
    