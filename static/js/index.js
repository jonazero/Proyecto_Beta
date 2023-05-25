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
        "y": ["../img/manos/2i.png"],
        "h": ["../img/manos/2i.png"],
        "n": ["../img/manos/2i.png"],
        "m": ["../img/manos/2i.png"],
        "u": ["../img/manos/2i.png"],
        "j": ["../img/manos/2i.png"],
        "7": ["../img/manos/2i.png"],
        "6": ["../img/manos/2i.png"],
    },
    mutex = {
        locked: false,
        queue: [],
        lock() {
            if (!this.locked) {
                this.locked = true;
                return Promise.resolve();
            } else {
                return new Promise(resolve => {
                    this.queue.push(resolve);
                });
            }
        },
        unlock() {
            if (this.queue.length > 0) {
                const resolve = this.queue.shift();
                resolve();
            } else {
                this.locked = false;
            }
        }
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

        // wait for ICE gathering to complete
        await new Promise((resolve) => {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                const checkState = () => {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                };
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });

        const response = await fetch('/offer_cv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sdp: pc.localDescription.sdp,
                type: pc.localDescription.type,
                video_transform: 'none'
            })
        });

        const answer = await response.json();
        await pc.setRemoteDescription(answer);
    } catch (e) {
        alert(e);
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
    dc.onclose = () => console.log("data channel closed");
    dc.onopen = () => console.log("data channel created");

    coordinate(0);
}

async function coordinate(stat) {
    first = sessionStorage.getItem("first");
    let benchmark_coords = new Object(),
        practice_coords = new Object(),
        camera_coords = new Object(),
        user_params = new Object();
    user_params = await getuserParams();
    if (first === "true" && stat === 0) {
        alert("Benchmark. \nPor favor escribe las siguientes oraciones para que el sistema determine tu desempeño.");
        sessionStorage.setItem('first', 'false');
        for (let index = 0; index < paragraphs.length; index++) {
            Object.assign(benchmark_coords, await loadParagraph(paragraphs[index]).then(res => waitForKeyPress(res, 0)));
        }
        stat = 1;
        sessionStorage.setItem('benchmark_coords', JSON.stringify(benchmark_coords))
    }
    else {
        stat = 1;
    }
    if (stat === 1) {
        alert("Camera. Escribe la oracion segun indique el dedo. \nEVITA HACERLO DEMASIADO RAPIDO")
        hands.style.display = "flex";
        for (let index = 0; index < paragraphs.length; index++) {
            Object.assign(camera_coords, await loadParagraph(paragraphs[index]).then(res => waitForKeyPress(res, 1)));
        }
        stat = 2;
        sessionStorage.setItem('camera_coords', JSON.stringify(camera_coords))
    }
    if (stat === 2) {
        alert("Practice. Escribe la oracion segun indique el dedo. \nEVITA HACERLO DEMASIADO RAPIDO")
        if (Object.entries(benchmark_coords === 0)) {
            benchmark_coords = JSON.parse(sessionStorage.getItem("benchmark_coords"));
        }
        console.log(GetImportantKeys(camera_coords, benchmark_coords, 0.030));
        console.log("h,g", euclideanDistance(camera_coords.h, camera_coords.g))
        console.log("h,j", euclideanDistance(camera_coords.h, camera_coords.j))
        console.log("h,y", euclideanDistance(camera_coords.h, camera_coords.y))
        console.log("h,b", euclideanDistance(camera_coords.h, camera_coords.b))
        console.log("h,n", euclideanDistance(camera_coords.h, camera_coords.n))

        /*
        try {
            const response = await fetch("/words/", {
                body: JSON.stringify({ letters: ["an", "es"], limit: 10 }),
                headers: { "Content-type": "application/json;charset=UTF-8" },
                method: "POST"
            });
            const data = await handleErrors(response).json();
            const words = data.words;
            console.log(words);
        } catch (error) {
            console.error(error.message);
        }
        */
    }
}
function GetImportantKeys(camera_coords, benchmark_coords, threshold_percentage) {
    const keysWithDiff = [];
    for (const key in camera_coords) {
        if (benchmark_coords.hasOwnProperty(key)) {
            const coords1 = camera_coords[key];
            const coords2 = benchmark_coords[key];
            distance = euclideanDistance(coords1, coords2);
            //console.log(key, coords1, coords2, distance);
            const totalDistance = euclideanDistance([0, 0], [100, 100]); // replace with actual total distance calculation
            const threshold = threshold_percentage / 100 * totalDistance;
            if (distance >= threshold) {
                keysWithDiff.push(key);
            }
        }
    }
    return keysWithDiff;
}


function euclideanDistance(point1, point2) {
    const deltaX = point2[0] - point1[0];
    const deltaY = point2[1] - point1[1];
    return Math.sqrt(deltaX * deltaX + deltaY * deltaY);
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
    const spanElements = typingText.querySelectorAll("span")
    const charIndexOffset = opt ? 0 : 1;
    const charElement = spanElements[charIndex + charIndexOffset];
    if (!charElement) {
        return;
    }
    const cf = charElement.innerText.toLowerCase();
    const images = fingerImages[cf] || [];
    if (images[0].includes("1")) {
        iiElement.src = images[0] || "../img/manos/1.png";
        idElement.src = "../img/manos/2.png"
    } else {
        idElement.src = images[0] || "../img/manos/2.png";
        iiElement.src = "../img/manos/1.png";
    }
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


function initTyping(kp) {
    let characters = typingText.querySelectorAll("span");
    if (charIndex <= characters.length) {
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
    try {
        let response = await fetch("/user/params", { headers: { "Authorization": "Bearer " + window.sessionStorage.getItem("jwt") } });
        let data = await handleErrors(response).json();
        return data;
    } catch (error) {
        console.error(error.message);
    }
}

function handleErrors(response) {
    if (!response.ok) {
        throw Error(response.status + ' ' + response.statusText);
    }
    return response;
}

async function waitForKeyPress(len, status) {
    let fingecoords = new Object();
    return new Promise(async resolve => {
        const onKeyDown = async event => {
            if (len >= 1) {
                showFinger(false);
            }
            initTyping(event.key);
            const timestamp = Date.now()
            dc.send(JSON.stringify({ key: event.key, status: status, timestamp: timestamp}));
            const data = await waitForMessage(dc, event.key);
            const msg = data;
            console.log(msg);
            if (msg == null) {
                alert("Verifique que las dos manos estén dentro del area de captura de la camra.");
            }
            else if ("error" in msg) {
                alert(msg.error);
                throw msg.error;
            } else {
                fingecoords[msg.key] = msg.coords;
                len--;
                if (len === 0) {
                    document.removeEventListener("keydown", onKeyDown);
                    reset();
                    resolve(fingecoords);
                }
            }
        };
        document.addEventListener("keydown", onKeyDown);
    });
}

function waitForMessage(dc, msgId) {
    return new Promise(resolve => {
        const handler = event => {
            const msg = JSON.parse(event.data);
            if (msg.key === msgId) {
                dc.removeEventListener('message', handler);
                resolve(msg);
            }
        };
        dc.addEventListener('message', handler);
    });
}


