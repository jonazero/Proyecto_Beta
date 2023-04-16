const typingText = document.querySelector(".typing-text p"),
    inpField = document.querySelector(".wrapper .input-field"),
    tryAgainBtn = document.querySelector(".content button"),
    timeTag = document.querySelector(".time span b"),
    mistakeTag = document.querySelector(".mistake span"),
    wpmTag = document.querySelector(".wpm span"),
    cpmTag = document.querySelector(".cpm span"),
    videoElement = document.querySelector('video'),
    videoSelect = document.querySelector('select#videoSource'),
    stadistics = document.querySelector(".content .result-details"),
    hands = document.querySelector(".hands"),
    audioElements = document.querySelectorAll('audio[id^="sound-"]'),
    selectors = [videoSelect];


var timer,
    maxTime = 600,
    timeLeft = maxTime,
    charIndex = mistakes = isTyping = 0,
    mainNav = document.getElementById('main-nav'),
    navbarToggle = document.getElementById('navbar-toggle'),
    generatedpan = "",
    pc = null,
    dc = null,
    constraints = null;


tryAgainBtn.addEventListener("click", reset);

function gotDevices(deviceInfos) {
    // Handles being called several times to update labels. Preserve values.
    const values = selectors.map(select => select.value);
    selectors.forEach(select => {
        while (select.firstChild) {
            select.removeChild(select.firstChild);
        }
    });
    for (let i = 0; i !== deviceInfos.length; ++i) {
        const deviceInfo = deviceInfos[i];
        const option = document.createElement('option');
        option.value = deviceInfo.deviceId;
        if (deviceInfo.kind === 'videoinput') {
            option.text = deviceInfo.label || `camera ${videoSelect.length + 1}`;
            videoSelect.appendChild(option);
        }
    }
    selectors.forEach((select, selectorIndex) => {
        if (Array.prototype.slice.call(select.childNodes).some(n => n.value === values[selectorIndex])) {
            select.value = values[selectorIndex];
        }
    });
}

function handleError(error) {
    console.log('navigator.MediaDevices.getUserMedia error: ', error.message, error.name);
}

function createPeerConnection() {
    var config = { sdpSemantics: "unified-plan" };
    config.iceServers = [
        {
            urls: ['stun:stun.l.google.com:19302'],
        },
        /*
        {
            urls: "turn:openrelay.metered.ca:80",
            username: "openrelayproject",
            credential: "openrelayproject",
        },
        {
            urls: "turn:openrelay.metered.ca:443",
            username: "openrelayproject",
            credential: "openrelayproject",
        },
        {
            urls: "turn:openrelay.metered.ca:443?transport=tcp",
            username: "openrelayproject",
            credential: "openrelayproject",
        },
        */
    ];
    pc = new RTCPeerConnection(config);

    // connect audio / video
    pc.addEventListener("track", function (evt) {
        if (evt.track.kind == "video")
            document.getElementById("video").srcObject = evt.streams[0];
    });
    return pc;
}

function negotiate() {
    return pc.createOffer().then(function (offer) {
        return pc.setLocalDescription(offer);
    }).then(function () {
        // wait for ICE gathering to complete
        return new Promise(function (resolve) {
            if (pc.iceGatheringState === "complete") {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === "complete") {
                        pc.removeEventListener("icegatheringstatechange", checkState);
                        resolve();
                    }
                }
                pc.addEventListener("icegatheringstatechange", checkState);
            }
        });
    })
        .then(function () {
            var offer = pc.localDescription;
            return fetch("/offer_cv", {
                body: JSON.stringify({ sdp: offer.sdp, type: offer.type, video_transform: 'none' }),
                headers: { "Content-Type": "application/json" },
                method: "POST",
            });
        }).then(function (response) {
            return response.json();
        }).then(function (answer) {
            return pc.setRemoteDescription(answer);
        }).catch(function (e) {
            alert(e);
        });
}
async function start() {
    pc = createPeerConnection();
    dc = pc.createDataChannel('chat');
    constraints = {
        audio: false,
        video: {
            deviceId: videoSelect.value, width: { min: 900, max: 1920 },
            height: { min: 700, max: 1080 }
        }
    };
    if (constraints.video) {
        navigator.mediaDevices.getUserMedia(constraints)
            .then(function (stream) {
                navigator.mediaDevices.enumerateDevices()
                    .then(gotDevices).catch(handleError);
                stream.getTracks().forEach(function (track) {
                    pc.addTrack(track, stream);
                });
                return negotiate();
            }, function (err) {
                alert(err);
            });
    } else {
        negotiate();
    }
    /*
    dc.onmessage = function (evt) {
        msg = JSON.parse(evt.data);
        if ('error' in msg) {
            alert(msg.error);
            throw msg.error;
        } else if (msg.status === 0) {
            let characters = typingText.querySelectorAll("span");
            if (characters[charIndex].innerText == msg.key) {
                benchmark_coords[msg.key] = msg.coords;
            }
            initTyping(msg.key);
        } else if (msg.status === 1) {
            showFinger();
            let characters = typingText.querySelectorAll("span");
            if (characters[charIndex].innerText == msg.key) {
                testing_coords[msg.key] = msg.coords;
            }
            initTyping(msg.key);
        }
    };
    */
    dc.onclose = function () {
        console.log("data channel closed");
    }
    dc.onopen = function () {
        console.log("data channel created");
    };
    let benchmark_coords = new Object(),
        testing_coords = new Object(),
        camera_coords = new Object(),
        user_params = new Object();
    user_params = await getuserParams();
    if (sessionStorage.getItem('first') === "true" || Object.keys(user_params.matriz_errores_promedio).length === 0) {
        alert("Benchmark. \nPor favor escribe las siguientes oraciones para que el sistema determine tu desempeño.");
        sessionStorage.setItem('first', 'false');
        for (let index = 0; index < paragraphs.length; index++) {
            await loadParagraph(paragraphs[index]).then(res => waitForKeyPress(res, 0));
        }
        alert("Escribe la oracion segun indique el dedo. \nEVITA HACERLO DEMASIADO RAPIDO")
        hands.style.display = "flex";
        for (let index = 0; index < paragraphs.length; index++) {
            await loadParagraph(paragraphs[index]).then(res => waitForKeyPress(res, 1));
        }
    } else if (Object.keys(user_params.matriz_errores_promedio).length !== 0) {
        alert("Escribe la oracion segun indique el dedo. \nEVITA HACERLO DEMASIADO RAPIDO")
        hands.style.display = "flex";
        for (let index = 0; index < paragraphs.length; index++) {
            await loadParagraph(paragraphs[index]).then(res => waitForKeyPress(res, 1));
        }
    }
}
videoSelect.onchange = function () {
    constraints = {
        audio: false,
        video: { deviceId: videoSelect.value, width: { min: 900, max: 1920 }, height: { min: 700, max: 1080 } }
    };
    if (constraints.video) {
        navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
            stream.getTracks().forEach(function (track) {
                pc.getSenders().forEach(function (sender) {
                    sender.replaceTrack(track);
                });
            });
        }, function (err) {
            alert(err);
        });
    }
}
function stop() {
    // close data channel
    if (dc) {
        dc.close();
    }
    // close transceivers
    if (pc.getTransceivers) {
        pc.getTransceivers().forEach(function (transceiver) {
            if (transceiver.stop) {
                transceiver.stop();
            }
        });
    }

    // close local audio / video
    pc.getSenders().forEach(function (sender) {
        sender.track.stop();
    });

    // close peer connection
    setTimeout(function () {
        pc.close();
    }, 500);
}

navbarToggle.addEventListener('click', function () {
    if (this.classList.contains('active')) {
        mainNav.style.display = "none";
        this.classList.remove('active');
    }
    else {
        mainNav.style.display = "flex";
        this.classList.add('active');

    }
});

function loadParagraph(sentence) {
    return new Promise(resolve => {
        typingText.innerHTML = "";
        sentence.split("").forEach(char => {
            let span = `<span>${char}</span>`
            typingText.innerHTML += span;
        });
        typingText.querySelectorAll("span")[0].classList.add("active");
        typingText.addEventListener("click", () => inpField.focus());
        showFinger();
        resolve(sentence.length);
    })
}

function showFinger(firstpressed) {
    let characters = typingText.querySelectorAll("span"),
        cf = null;
    if (charIndex < characters.length - 1) {
        if (firstpressed == true) {
            cf = typingText.querySelectorAll("span")[charIndex].innerText;
        } else {
            cf = typingText.querySelectorAll("span")[charIndex + 1].innerText;
        }

    }
    document.getElementById("ii").src = "../img/manos/1.png";
    document.getElementById("id").src = "../img/manos/2.png";
    if (cf == null) { }
    else if (cf == ' ') {
        document.getElementById("ii").src = "../img/manos/1p.png";
        document.getElementById("id").src = "../img/manos/2p.png";
    } else if (cf == '1' || cf == 'q' || cf == 'z' || cf == 'a') {
        document.getElementById("ii").src = "../img/manos/1m.png";
    } else if (cf == '2' || cf == 'x' || cf == 'w' || cf == 's') {
        document.getElementById("ii").src = "../img/manos/1a.png";
    } else if (cf == '3' || cf == 'c' || cf == 'd' || cf == 'e') {
        document.getElementById("ii").src = "../img/manos/1med.png";
    } else if (cf == '5' || cf == '4' || cf == 'v' || cf == 'b' || cf == 'g' || cf == 't' || cf == 'r' || cf == 'f') {
        document.getElementById("ii").src = "../img/manos/1i.png";
    } else if (cf == '0' || cf == 'ñ' || cf == 'p') {
        document.getElementById("id").src = "../img/manos/2m.png";
    } else if (cf == '9' || cf == '.' || cf == 'l' || cf == 'o') {
        document.getElementById("id").src = "../img/manos/2a.png";
    } else if (cf == '8' || cf == ',' || cf == 'k' || cf == 'i') {
        document.getElementById("id").src = "../img/manos/2med.png";
    } else {
        document.getElementById("id").src = "../img/manos/2i.png";
    }
}

function sendNormalChar(event) {
    let status = event.currentTarget.myparam;
    showFinger(false);
    inpField.focus();
    dc.send(JSON.stringify({ "key": event.key, "status": status }));
};

function playSound(id) {
    const audioElement = document.getElementById(id);
    resetSound();
    if (audioElement.paused) {
        audioElement.play();
    }
};

function resetSound() {
    audioElements.forEach(audioElement => {
        audioElement.pause();
        audioElement.currentTime = 0;
    });
};


function initTyping(kp) {
    let characters = typingText.querySelectorAll("span");
    if (charIndex < characters.length) {
        if (!isTyping) {
            timer = setInterval(initTimer, 1000);
            isTyping = true;
        }
        if (kp == null) {
            if (charIndex > 0) {
                charIndex--;
                if (characters[charIndex].classList.contains("incorrect")) {
                    mistakes--;
                }
                characters[charIndex].classList.remove("correct", "incorrect");
            }
        } else {
            if (characters[charIndex].innerText == kp) {
                characters[charIndex].classList.add("correct");
                playSound('sound-key');
            } else {
                mistakes++;
                characters[charIndex].classList.add("incorrect");
                playSound('sound-mistake')
            }
            charIndex++;
        }
        characters.forEach(span => span.classList.remove("active"));
        if (charIndex < characters.length - 1) {
            characters[charIndex].classList.add("active");
        }
        let wpm = Math.round(((charIndex - mistakes) / 5) / (maxTime - timeLeft) * 60);
        wpm = wpm < 0 || !wpm || wpm === Infinity ? 0 : wpm;

        wpmTag.innerText = wpm;
        mistakeTag.innerText = mistakes;
        cpmTag.innerText = charIndex - mistakes;
    } else {
    }
}

function initTimer() {
    if (timeLeft > 0) {
        timeLeft--;
        timeTag.innerText = timeLeft;
        let wpm = Math.round(((charIndex - mistakes) / 5) / (maxTime - timeLeft) * 60);
        wpmTag.innerText = wpm;
    } else {
        clearInterval(timer);
    }
}

function reset() {
    clearInterval(timer);
    timeLeft = maxTime;
    charIndex = mistakes = isTyping = 0;
    inpField.value = "";
    timeTag.innerText = timeLeft;
    wpmTag.innerText = 0;
    mistakeTag.innerText = 0;
    cpmTag.innerText = 0;
}

async function getuserParams() {
    let response = await fetch("/user/params", { headers: { "Authorization": "Bearer " + window.sessionStorage.getItem("jwt") } })
    let data = await handleErrors(response);
    return data;
}

async function handleErrors(response) {
    let jsonresponse;
    jsonresponse = await response.json();
    console.log(jsonresponse);
    if (!response.ok) {
        alert(jsonresponse.detail);
        throw Error(response.statusText);
    }
    return jsonresponse;
}

async function waitForKeyPress(len, status) {
    return new Promise(resolve => {
        const onKeyDown = (event) => {
            console.log(len);
            if (len === 1) {
                document.removeEventListener('keydown', onKeyDown);
                reset();
                resolve();

            }
            else {
                dc.send(JSON.stringify({ "key": event.key, "status": status }));
                showFinger();
                waitForMessage(dc).then(data => {
                    msg = JSON.parse(data);
                    if ('error' in msg) {
                        alert(msg.error);
                        throw msg.error;
                    } else {
                        initTyping(event.key);
                        len--;
                    }
                });
            }
        }
        document.addEventListener('keydown', onKeyDown);
    });
}

function waitForMessage(dc) {
    return new Promise(resolve => {
        dc.onmessage = event => {
            resolve(event.data);
        };
    });
}

