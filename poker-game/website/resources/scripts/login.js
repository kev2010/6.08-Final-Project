import { setCookie } from './cookies.js';

// Get the modal
var modal = document.getElementById('id01');

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

document.getElementById('login').onsubmit = function() { 
    username = document.getElementById('username').value;
    password = document.getElementById('password').value;

    if (isValidLogin(username, password)) {
        setCookie('user', username, 365);
    }
    
    return false;
}

const isValidLogin = (username, password) => {
    let xhttp = new XMLHttpRequest();
    var params = `username=${username}&password=${password}`;
    //  TODO: CHANGE THIS URL
    let url = "http://608dev-2.net/sandbox/sc/team079/team079/poker-game/request_handler.py";
    
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // XMLHttp will provide the servers response as text,s we need to parse to turn it into JSON
            let response = JSON.parse(this.response); // 89

            // Press f12 to see the console.log and see the full response body from the poker api
            console.log(response);
            let to_display = JSON.stringify(response);
            let valid = respone.valid;
            return (valid === "True");
        } else {
            throw "Login GET request failed!";
        }
    }
    xhttp.open("GET", url+"?"+params, true);
    xhttp.send(null);
}