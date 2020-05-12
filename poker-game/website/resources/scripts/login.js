// import { setCookie } from './cookies.js';

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
        login = document.getElementById('login-button');
        login.hidden = true;
        logout = document.getElementById('logout-button');
        logout.hidden = false;
    }

    return false;
}

const isValidLogin = (username, password) => {
    let xhttp = new XMLHttpRequest();
    var params = `username=${username}&password=${password}`;
    //  TODO: CHANGE THIS URL
    let url = "http://608dev-2.net/sandbox/sc/team079/team079/rooms_infra/Python_Files/authentication.py?";
    
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // XMLHttp will provide the servers response as text,s we need to parse to turn it into JSON
            let response = JSON.parse(this.response); // 89

            // Press f12 to see the console.log and see the full response body from the poker api
            console.log(response);
            return (response === 1);
        } else {
            throw "Login GET request failed!";
        }
    }
    xhttp.open("GET", url+params, true);
    xhttp.send(null);
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
    console.log("asdfs");
    console.log(document.cookie);
}
