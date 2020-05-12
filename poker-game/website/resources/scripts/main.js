// import { getCookie } from './cookies.js';

const suitHTML = {
    "s": "&spades;",
    "h": "&hearts;",
    "d": "&diams;",
    "c": "&clubs;"
}

var roomID = '';

document.getElementById('room-id').onsubmit = function() { 
    roomID = document.getElementById('room').value;
    return false;
}

const display = () => {
    let xhttp = new XMLHttpRequest();
    let user = getUser();
    // let user = '';
    var params = `user=${user}&type=spectate&room_id=${roomID}`;
    console.log(roomID);
    //  URL for PokerAPI
    let url = "http://608dev-2.net/sandbox/sc/team079/team079/poker-game/request_handler.py?";
    
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // XMLHttp will provide the servers response as text,s we need to parse to turn it into JSON
            console.log(this.response);
            let response = JSON.parse(this.response); // 89

            // Press f12 to see the console.log and see the full response body from the poker api
            console.log(response);
            let to_display = JSON.stringify(response);

            if (response.players.length != 0) {
                players = response.players;
                for (var i = 0; i < players.length; i++) {
                    var elt = document.getElementById("seat" + (i+1));
                    var cards = '';
                    if (players[i].cards === 'hidden') {
                        cards = ['  ', '  '];
                    } else if (players[i].cards === '') {
                        cards = "Folded";
                    } else {
                        var cards = players[i].cards.split(',');
                    }
                    elt.innerHTML = `
                        <td>${players[i].user}</td>
                        <td>${players[i].bal}</td>
                        <td>${players[i].bet}</td>
                        <td>${(cards.length == 2) ? displayHoleCards(cards) : "Folded"}</td>
                    `;
                }
            }

            if (response.state.length != 0) {
                gameState = response.state[0];
                //  If there is a game going on
                if (gameState.length != 0) {
                    displayBoard(gameState);
                    displayDealer(gameState);
                    displayAction(gameState);
                    displayPot(gameState);
                }
            }

            // Now, target the DIV in question, and set the innerHTML to the response
            let targetDiv = document.getElementById("instructor-answer");
            targetDiv.innerHTML = to_display;
        }
    }

    xhttp.open("GET", url+params, true);
    xhttp.send(null);
}

const getUser = () => {
    return getCookie("user");
}

const displayBoard = (gameState) => {
    let board = gameState.board.split(',');
    let streets = ['flop1', 'flop2', 'flop3', 'turn', 'river']

    for (var i = 0; i < streets.length; i++) {
        var showCard = false;
        if (board.length >= (i+1)) {
            showCard = true;
        }
        card = streets[i]
        var elt = document.getElementById(card);
        var eltRank = document.getElementById(card + '-rank');
        var eltSuit = document.getElementById(card + '-suit');
        elt.hidden = !showCard;
        if (showCard) {
            eltRank.innerHTML = board[i][0];
            eltSuit.innerHTML = suitHTML[board[i][1]];

            if (board[i][1] === 's' || board[i][1] === 'c') {
                eltRank.className = 'card-text black';
                eltSuit.className = 'card-img black';
            } else {
                eltRank.className = 'card-text red';
                eltSuit.className = 'card-img red';
            }
        }
    }
}

const displayDealer = (gameState) => {
    let dealer = gameState.dealer;
    var elt = document.getElementById("seat" + (dealer+1));
    elt.innerHTML += `<td>O</td>`;
}

const displayAction = (gameState) => {
    let action = gameState.action;
    var elt = document.getElementById("seat" + (action+1));
    elt.innerHTML += `<td><------</td>`;
}

const displayPot = (gameState) => {
    let pot = gameState.pot;
    var elt = document.getElementById("pot");
    elt.innerHTML = `POT TOTAL: ${pot}`;
}

const displayHoleCards = (cards) => {
    result = ""
    for (var i = 0; i < cards.length; i++) {
        var rank = cards[i][0];
        var suit = cards[i][1];
        var suitHTML = "";
        var color = ""

        if (suit === 's' || suit === 'c') {
            suitHTML = (suit === 's') ? "&spades;" : "&clubs;";
            color = "black";
        } else if (suit === 'h' || suit === 'd') {
            suitHTML = (suit === 'h') ? "&hearts;" : "&diams;";
            color = "red";
        } else {
            suitHTML = "";
            color = "black";
        }
        result += `
        <div class="card-small" id="flop2">
            <p class="card-text ${color}">${rank}</p>
            <p class="card-img ${color}">${suitHTML}</p>
        </div>
        `
    }
    return result;
}

window.onload = display;

setInterval(function(){
    console.log("refreshing");
    display();
},1000);


// //  COOKIES
// function setCookie(cname, cvalue, exdays) {
//     var d = new Date();
//     d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
//     var expires = "expires="+d.toUTCString();
//     document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
// }


function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

