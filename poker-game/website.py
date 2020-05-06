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
                    <p> These are _____'s cards. Insert a user param in the URL to see someone's cards</p>
                    <div class="table">
                        <div class="board">
                            <div class="card-small" id="card1">
                                <p class="card-text black">A</p>
                                <p class="card-img black">&clubs;</p>
                            </div>
                            <div class="card-small" id="card2">
                                <p class="card-text black">10</p>
                                <p class="card-img black">&spades;</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="instructor-answer"></div>
            </body>

            <script>
                function joke() {
                    let xhttp = new XMLHttpRequest();
                    var params = JSON.stringify({ 'type': 'spectate' });
                    let url = "http://608dev-2.net/sandbox/sc/team079/team079/poker-game/request_handler.py";

                    xhttp.onreadystatechange = function() {
                        if (this.readyState == 4 && this.status == 200) {
                            // XMLHttp will provide the servers response as text, we need to parse to turn it into JSON
                            console.log(response);
                            let response = JSON.parse(this.response); // 89

                            // Press f12 to see the console.log and see the full response body from the jokes api, there
                            //  is a lot of other information we can use, for this example, I just care about the text of
                            //  the joke!
                            let jokeText = 'test';
                            
                            // Now, target the DIV in question, and set the innerHTML to the jokeText
                            let targetDiv = document.getElementById("instructor-answer");
                            targetDiv.innerHTML = jokeText;
                        }
                    }

                    xhttp.open("GET", url, true);
                    xhttp.send(params);
                }

                window.onload = joke;

                setInterval(function(){
                    console.log("refreshing");
                    joke();
                },1000);
            </script>
        '''
    

