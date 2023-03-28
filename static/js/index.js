const videoElement = document.querySelector('video');
const videoSelect = document.querySelector('select#videoSource');
const selectors = [videoSelect];

const typingText = document.querySelector(".typing-text p"),
  inpField = document.querySelector(".wrapper .input-field"),
  tryAgainBtn = document.querySelector(".content button"),
  timeTag = document.querySelector(".time span b"),
  mistakeTag = document.querySelector(".mistake span"),
  wpmTag = document.querySelector(".wpm span"),
  cpmTag = document.querySelector(".cpm span");


let timer,
  maxTime = 600,
  timeLeft = maxTime,
  charIndex = mistakes = isTyping = 0;

let mainNav = document.getElementById('main-nav');
let navbarToggle = document.getElementById('navbar-toggle');

// peer connection
var pc = null;

// data channel
var dc = null;

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
  let received;
  pc = createPeerConnection();
  dc = pc.createDataChannel('chat');
  dc.onclose = function () {
    console.log("data channel closed");
  }
  dc.onopen = function () {
    console.log("data channel created");
  };
  dc.onmessage = function (evt) {
    if (evt.data) {
      received = JSON.parse(evt.data)
      if (received.error == true && received.first == true) {
        alert(received.error_name);
      } else if (received.error == false && received.first == true) {
        initTyping(received.key);
      } else {
        document.querySelectorAll('.result-details').forEach(function (el) {
          el.style.display = "flex";
        });
        document.querySelectorAll('.content').forEach(function (el) {
          el.style.display = "flex";
        });
        cf = typingText.querySelectorAll("span")[charIndex + 1].innerText;
        showFinger(cf);
        initTyping(received.key);
      }
    }
  };
  const videoSource = videoSelect.value;
  const constraints = {
    audio: false,
    video: { deviceId: videoSource, width: { min: 900, max: 1920 }, height: { min: 700, max: 1080 } }
  };
  if (constraints.video) {
    //navigator.mediaDevices.getUserMedia(constraints).then(gotStream).then(gotDevices).catch(handleError);
    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
      stream.getTracks().forEach(function (track) {
        navigator.mediaDevices.enumerateDevices().then(gotDevices).catch(handleError);
        pc.addTrack(track, stream);
      });
      return negotiate();
    }, function (err) {
      alert(err);
    });

  } else {
    negotiate();
  }
}
videoSelect.onchange = function () {
  pc.getSenders().forEach(function (sender) {
    sender.track.stop();
  });
  start();
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

function loadParagraph(par_index) {
  typingText.innerHTML = "";
  paragraphs[par_index].split("").forEach(char => {
    let span = `<span>${char}</span>`
    typingText.innerHTML += span;
  });
  typingText.querySelectorAll("span")[0].classList.add("active");
  document.addEventListener("keypress", sendNormalChar);
  typingText.addEventListener("click", () => inpField.focus());
}

function showFinger(cf) {
  document.getElementById("ii").src = "../img/manos/1.png";
  document.getElementById("id").src = "../img/manos/2.png";
  if (cf == ' ') {
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
  inpField.focus();
  dc.send(event.key);
};

function playSound(id) {
  const audioElement = document.getElementById(id);
  resetAll();
  if (audioElement.paused) {
    audioElement.play();
  }
};

function resetAll() {
  const audioElements = document.querySelectorAll('audio[id^="sound-"]');
  audioElements.forEach(audioElement => {
    audioElement.pause();
    audioElement.currentTime = 0;
  });
};


function initTyping(kp) {
  let characters = typingText.querySelectorAll("span");
  if (charIndex < characters.length - 1 && timeLeft > 0) {
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
    characters[charIndex].classList.add("active");

    let wpm = Math.round(((charIndex - mistakes) / 5) / (maxTime - timeLeft) * 60);
    wpm = wpm < 0 || !wpm || wpm === Infinity ? 0 : wpm;

    wpmTag.innerText = wpm;
    mistakeTag.innerText = mistakes;
    cpmTag.innerText = charIndex - mistakes;
    console.log(charIndex, characters.length);
  } else {
    dc.send("benchmark")
    resetGame();
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

function resetGame() {
  loadParagraph(1);
  clearInterval(timer);
  timeLeft = maxTime;
  charIndex = mistakes = isTyping = 0;
  inpField.value = "";
  timeTag.innerText = timeLeft;
  wpmTag.innerText = 0;
  mistakeTag.innerText = 0;
  cpmTag.innerText = 0;
}

loadParagraph(0);
tryAgainBtn.addEventListener("click", resetGame);
