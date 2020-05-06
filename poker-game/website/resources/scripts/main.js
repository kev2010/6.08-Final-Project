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