const display = () => {
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
                    displayBoard(gameState);
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

const displayBoard = (gameState) => {
    let board = gameState.board.split(',');
    let streets = ['flop1', 'flop2', 'flop3', 'turn', 'river']

    for (i = 0; i < streets.length; i++) {
        var showCard = false;
        if (board.length >= (i+1)) {
            showCard = true;
        }
        card = streets[i]
        var elt = document.getElementById(card);
        var eltRank = document.getElementById(card + '-rank');
        // var eltSuit = document.getElementById(card + '-suit');
        elt.hidden = !showCard;
        if (showCard) {
            eltRank.innerHTML = board[i][0];
        }
    }
}

window.onload = display;

setInterval(function(){
    console.log("refreshing");
    display();
},1000);