const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');
const form_signup = document.getElementById('form-signup');
const form_login = document.getElementById('form-login');

signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});


function send() {
    var url = window.location.search;
    const urlParams = new URLSearchParams(url);
    if (urlParams.has("code") && urlParams.has("scope")) {
        var req = new XMLHttpRequest();
        req.onreadystatechange = function () {
            if (req.readyState === 4) {
                if (req.response["result"] === true) {
                    window.sessionStorage.setItem('jwt', req.response["access_token"]);
                    window.sessionStorage.setItem('refresh', req.response["refresh_token"]);
                    window.sessionStorage.setItem('first', 'true');
                    window.location = "/camara";
                }
            }
        }
        req.withCredentials = true;
        req.responseType = 'json';
        req.open("get", "/auth/google-token?" + url.substring(1), true);
        req.send("");
    }
}

form_signup.addEventListener('submit', function (e) {
    e.preventDefault();
    const user = new FormData(form_signup);
    if (user.get('email') == '' || user.get('pwd') == '' || user.get('name') == '') {
        alert("El nombre, email o contraseña no pueden estar vacios");
        return
    }
    fetch("/auth/create-user", {
        body: JSON.stringify({ username: user.get("name"), email: user.get("email"), pwd: user.get("pwd"), keyData: []}),
        headers: { "Content-type": "application/json;charset=UTF-8" },
        method: "POST"
    })
        .then(handleErrors)
        .then(response => {
            fetch("/auth/token", {
                body: JSON.stringify({ email: user.get("email"), pwd: user.get("pwd") }),
                headers: { "Content-type": "application/json;charset=UTF-8" },
                method: "POST"
            })
                .then(handleErrors)
                .then(r => {
                    if (r['result'] == true) {
                        window.sessionStorage.setItem('jwt', r["access_token"]);
                        window.sessionStorage.setItem('first', 'true');
                        window.location = "/camara";
                    }
                })
                .catch(err => console.log(err));
        })
        .catch(error => console.log(error));
})

form_login.addEventListener('submit', function (e) {
    e.preventDefault();
    const user = new FormData(form_login);
    if (user.get('email') == '' || user.get('pwd') == '') {
        throw Error("El email o contraseña no pueden estar vacios");
    }
    fetch("/auth/token", {
        body: JSON.stringify({ email: user.get("email"), pwd: user.get("pwd") }),
        headers: { "Content-type": "application/json;charset=UTF-8" },
        method: "POST"
    })
        .then(handleErrors)
        .then(r => {
            if (r['result'] == true) {
                window.sessionStorage.setItem('jwt', r["access_token"]);
                window.sessionStorage.setItem('first', 'true');
                window.location = "/camara";
            }
        })
        .catch(err => console.log(err));

})

async function handleErrors(response) {
    let jsonresponse;
    jsonresponse = await response.json();
    if (!response.ok) {
        alert(jsonresponse.detail);
        throw Error(response.statusText);
    }
    return jsonresponse;
}

