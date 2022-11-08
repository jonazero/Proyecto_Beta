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

function start() {
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
      initTyping(evt.data);
      evt.data = "";
      inpField.focus();
    };
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

function loadParagraph() {
  const ranIndex = Math.floor(Math.random() * paragraphs.length);
  typingText.innerHTML = "";
  paragraphs[ranIndex].split("").forEach(char => {
    let span = `<span>${char}</span>`
    typingText.innerHTML += span;
  });
  typingText.querySelectorAll("span")[0].classList.add("active");
  document.addEventListener("keypress", presion);
  typingText.addEventListener("click", () => inpField.focus());
}

function presion(event) {
  dc.send(event.charCode.toString());
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
      } else {
        mistakes++;
        characters[charIndex].classList.add("incorrect");
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
  } else {
    clearInterval(timer);
    inpField.value = "";
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
  loadParagraph();
  clearInterval(timer);
  timeLeft = maxTime;
  charIndex = mistakes = isTyping = 0;
  inpField.value = "";
  timeTag.innerText = timeLeft;
  wpmTag.innerText = 0;
  mistakeTag.innerText = 0;
  cpmTag.innerText = 0;
}

loadParagraph();
tryAgainBtn.addEventListener("click", resetGame);
