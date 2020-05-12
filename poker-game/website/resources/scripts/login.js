// import { setCookie } from './cookies.js';

// // Get the modal
// var modal = document.getElementById('login-button');

// // When the user clicks anywhere outside of the modal, close it
// window.onclick = function(event) {
//     if (event.target == modal) {
//         modal.style.display = "none";
//     }
// }

const updateLogin = () => {
    //  Change display for login/logout
    var loginButton = document.getElementById('login-button');
    var logoutButton = document.getElementById('logout-button');
    loginButton.hidden = getCookie("user") != "";
    logoutButton.hidden = getCookie("user") === "";
}

var logoutButton = document.getElementById('logout-button');
logoutButton.onclick = () => {
    setCookie('user', "", 365);
    updateLogin();
}

updateLogin();

var loginInfo = document.getElementById("login");
function handleForm(event) { event.preventDefault(); } 
loginInfo.addEventListener('submit', handleForm);

loginInfo.onsubmit = async function() { 
    username = document.getElementById('username').value;
    password = document.getElementById('password').value;
    console.log(isValidLogin(username, password));
    let login = await isValidLogin(username, password);
    // login = Promise.resolve(isValidLogin(username, password));
    // login.then((valid) => {
    console.log('async');
    if (login) {
        console.log('setting cookie');
        setCookie('user', username, 365);
        updateLogin();
    }
    // });
    console.log("hi");
    // isValidLogin(username, password).then(valid => {
    //     if (valid) {
    //         console.log('setting cookie');
    //         setCookie('user', username, 365);
    //         login = document.getElementById('login-button');
    //         login.hidden = true;
    //         logout = document.getElementById('logout-button');
    //         logout.hidden = false;
    //     }
    // })

    return false;
}

const isValidLogin = (username, password) => {
    return new Promise((resolve, reject) => {
        let xhttp = new XMLHttpRequest();
        var params = `username=${username}&password=${password}`;
        let url = "http://608dev-2.net/sandbox/sc/team079/team079/rooms_infra/Python_Files/authentication.py?";
        xhttp.open("GET", url+params, true);
        xhttp.onload = () => {
            if (this.status >= 200 && this.status < 300) {
                 // XMLHttp will provide the servers response as text,s we need to parse to turn it into JSON
                let response = JSON.parse(this.response); // 89

                // Press f12 to see the console.log and see the full response body from the poker api
                console.log(response);
                console.log(typeof(response));
                console.log(response === 1);
                console.log(typeof 1);

                // return new Promise((resolve, reject) => {
                //     var val = response === 1;
                //     resolve(val);
                // });
                resolve(response === 1);
            } else {
                reject({
                    status: this.status,
                    statusText: xhttp.statusText
                });
            }
        }
        xhttp.onerror = function () {
            reject({
                status: this.status,
                statusText: xhr.statusText
            });
        };
        xhttp.send();
 
    });



    // // return true;
    // let xhttp = new XMLHttpRequest();
    // var params = `username=${username}&password=${password}`;
    // //  TODO: CHANGE THIS URL
    // let url = "http://608dev-2.net/sandbox/sc/team079/team079/rooms_infra/Python_Files/authentication.py?";
    
    // xhttp.onreadystatechange = function() {
    //     if (this.readyState == 4 && this.status == 200) {
    //         // XMLHttp will provide the servers response as text,s we need to parse to turn it into JSON
    //         let response = JSON.parse(this.response); // 89

    //         // Press f12 to see the console.log and see the full response body from the poker api
    //         console.log(response);
    //         console.log(typeof(response));
    //         console.log(response === 1);
    //         console.log(typeof 1);

    //         // return new Promise((resolve, reject) => {
    //         //     var val = response === 1;
    //         //     resolve(val);
    //         // });
    //         return response === 1;
    //     }
    // }
    // xhttp.open("GET", url+params, true);
    // xhttp.send(null);
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
    console.log("asdfs");
    console.log(document.cookie);
}

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
