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


async function start() {
    var url = window.location.search;
    if (url.includes("code") && url.includes("prompt=consent") && url.includes("scope")) {
        const access_token = await getAccessToken(url);
        const user_info = await getUserInfo(access_token);
        console.log(user_info);
    }
}

async function getAccessToken(query_string) {
    const url_params = new URLSearchParams(query_string);
    const code = url_params.get('code');
    const scope = url_params.get('scope');
    try {
        const response = await fetch("http://localhost:8000/get-access-token?" + new URLSearchParams({
            code: code,
            scope: scope,
            authuser: 0,
            prompt: "consent"
        }), {
            method: "GET",
            headers: { "Content-type": "application/json;charset=UTF-8" }
        });
        const r = await response.json();
        return r["access_token"];
    } catch (error) {
        console.log(error);
    }
}

async function getUserInfo(access_token) {
    fetch("https://www.googleapis.com/oauth2/v3/userinfo", {
        method: "GET",
        headers: {
            "Content-type": "application/json;charset=UTF-8",
            "Authorization": `Bearer ${access_token}`
        }
    })
        .then(response => response.json())
        .then(r => console.log(r))
        .catch(err => console - loadParagraph(err));
}

form_signup.addEventListener('submit', function (e) {
    e.preventDefault();
    const user = new FormData(form_signup);

    fetch("/get-user-email", {
        body: JSON.stringify(user.get("email")),
        headers: { "Content-type": "application/json;charset=UTF-8" },
        method: "POST"
    })
        .then(res => res.json())
        .then(r => {
            if (r == "") {
                fetch("/create-user", {
                    body: JSON.stringify({ username: user.get("name"), email: user.get("email"), pwd: user.get("pwd"), matriz_errores_promedio: {}, matriz_tiempo_teclas: {}, wpm: 0, age: 0 }),
                    headers: { "Content-Type": "application/json" },
                    method: "POST"
                })
                    .then(response => response.json())
                    .then(json => console.log(json))
                    .catch(err => console.log(err));
            } else {
                alert("Ya hay un usuario registrado con este correo");
            }
        })
        .then(err => console.log(err))

});

form_login.addEventListener('submit', function (e) {
    e.preventDefault();
    const user = new FormData(form_login);
    alert(user.get("email"));
    fetch("/get-user-email", {
        body: JSON.stringify(user.get("email")),
        headers: { "Content-type": "application/json;charset=UTF-8" },
        method: "POST"
    })
        .then(response => response.json())
        .then(r => {
            if (r[0].pwd != "google" && r[0].pwd == user.get("pwd")) {
                location.assign("/camara");
            } else {
                alert("El usuario no existe")
            }
        })
        .catch(err => console.log(err))

})




