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
    selectors = [videoSelect],
    iiElement = document.getElementById("ii"),
    idElement = document.getElementById("id"),
    spanElements = typingText.querySelectorAll("span")
    fingerImages = {
    " ": ["../img/manos/1p.png", "../img/manos/2p.png"],
    "1": ["../img/manos/1m.png"],
    "q": ["../img/manos/1m.png"],
    "z": ["../img/manos/1m.png"],
    "a": ["../img/manos/1m.png"],
    "2": ["../img/manos/1a.png"],
    "x": ["../img/manos/1a.png"],
    "w": ["../img/manos/1a.png"],
    "s": ["../img/manos/1a.png"],
    "3": ["../img/manos/1med.png"],
    "c": ["../img/manos/1med.png"],
    "d": ["../img/manos/1med.png"],
    "e": ["../img/manos/1med.png"],
    "5": ["../img/manos/1i.png"],
    "4": ["../img/manos/1i.png"],
    "v": ["../img/manos/1i.png"],
    "b": ["../img/manos/1i.png"],
    "g": ["../img/manos/1i.png"],
    "t": ["../img/manos/1i.png"],
    "r": ["../img/manos/1i.png"],
    "f": ["../img/manos/1i.png"],
    "0": ["../img/manos/2m.png"],
    "ñ": ["../img/manos/2m.png"],
    "p": ["../img/manos/2m.png"],
    "9": ["../img/manos/2a.png"],
    ".": ["../img/manos/2a.png"],
    "l": ["../img/manos/2a.png"],
    "o": ["../img/manos/2a.png"],
    "8": ["../img/manos/2med.png"],
    ",": ["../img/manos/2med.png"],
    "k": ["../img/manos/2med.png"],
    "i": ["../img/manos/2med.png"],
};


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

async function negotiate() {
    try {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        // Wait for ICE gathering to complete
        await new Promise(resolve => {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function onIceGatheringStateChange() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', onIceGatheringStateChange);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', onIceGatheringStateChange);
            }
        });
        return pc.localDescription;
    } catch (error) {
        console.error('Error negotiating WebRTC connection:', error);
        return null;
    }
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
        alert("Camara. Escribe la oracion segun indique el dedo. \nEVITA HACERLO DEMASIADO RAPIDO")
        hands.style.display = "flex";
        for (let index = 0; index < paragraphs.length; index++) {
            await loadParagraph(paragraphs[index]).then(res => waitForKeyPress(res, 1));
        }
        reset()
        alert("Palabras.Escribe la oracion segun indique el dedo.")
        for (let index = 0; index < paragraphs.length; index++) {
            await loadParagraph(paragraphs[index]).then(res => waitForKeyPress(res, 1));
        }
    } else if (Object.keys(user_params.matriz_errores_promedio).length !== 0) {
        alert("Palabras.Escribe la oracion segun indique el dedo. \nEVITA HACERLO DEMASIADO RAPIDO")
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
        resolve(sentence.length);
        showFinger(true);
    })
}

function showFinger(opt) {
    const charIndexOffset = opt ? 0 : 1;
    const charElement = spanElements[charIndex + charIndexOffset];
    if (!charElement) {
        return;
    }
    const cf = charElement.innerText.toLowerCase();
    console.log(cf);
    const images = fingerImages[cf] || [];
    iiElement.src = images[0] || "../img/manos/1.png";
    idElement.src = images[1] || "../img/manos/2.png";
}

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


function initTyping(keyPressed) {
    const characters = typingText.querySelectorAll("span");
    const maxCharIndex = characters.length - 1;

    // Validate the input parameter
    if (keyPressed && typeof keyPressed !== "string" && keyPressed.length !== 1) {
        throw new Error("Invalid input");
    }

    // Move back one character if no key is pressed
    if (!keyPressed && charIndex > 0) {
        charIndex--;
        const prevChar = characters[charIndex];
        if (prevChar.classList.contains("incorrect")) {
            mistakes--;
        }
        prevChar.classList.remove("correct", "incorrect");
    }

    // Move forward one character if a key is pressed
    if (keyPressed && charIndex <= maxCharIndex) {
        const currentChar = characters[charIndex];
        if (currentChar.innerText === keyPressed) {
            currentChar.classList.add("correct");
            playSound('sound-key');
        } else {
            mistakes++;
            currentChar.classList.add("incorrect");
            playSound('sound-mistake')
        }
        charIndex++;
    }

    // Update the active class
    characters.forEach(span => span.classList.remove("active"));
    if (charIndex < maxCharIndex) {
        characters[charIndex].classList.add("active");
    }

    // Calculate and display the WPM, mistakes, and CPM
    const wpm = calculateWpm(charIndex, mistakes, maxTime, timeLeft);
    wpmTag.innerText = wpm || 0;
    mistakeTag.innerText = mistakes;
    cpmTag.innerText = charIndex - mistakes;
}

function calculateWpm(charIndex, mistakes, maxTime, timeLeft) {
    const totalChars = charIndex - mistakes;
    const elapsedTime = maxTime - timeLeft;
    if (totalChars === 0 || elapsedTime === 0) {
        return 0;
    }
    const wpm = Math.round(totalChars / 5 / (elapsedTime / 60));
    return isFinite(wpm) ? wpm : 0;
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
            if (len >= 1) {
                showFinger(false);
            }
            console.log("este es len: ", len);
            dc.send(JSON.stringify({ "key": event.key, "status": status }));
            waitForMessage(dc).then(data => {
                msg = JSON.parse(data);
                if ('error' in msg) {
                    alert(msg.error);
                    throw msg.error;
                } else {
                    initTyping(event.key);
                    len--;
                    if (len === 0) {
                        document.removeEventListener('keydown', onKeyDown);
                        reset();
                        resolve();
                    }
                }
            });
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

