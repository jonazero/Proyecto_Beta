const typingText = document.querySelector(".typing-text p"),
  inpField = document.querySelector(".wrapper .input-field"),
  tryAgainBtn = document.querySelector(".content button"),
  timeTag = document.querySelector(".time span b"),
  mistakeTag = document.querySelector(".mistake span"),
  wpmTag = document.querySelector(".wpm span"),
  cpmTag = document.querySelector(".cpm span"),
  videoElement = document.querySelector("video"),
  videoSelect = document.querySelector("select#videoSource"),
  stadistics = document.querySelector(".content .result-details"),
  hands = document.querySelector(".hands"),
  audioElements = document.querySelectorAll('audio[id^="sound-"]'),
  selectors = [videoSelect],
  iiElement = document.getElementById("ii"),
  spinwrap = document.querySelector(".page-wrapper"),
  idElement = document.getElementById("id"),
  fliphor = document.getElementById("btn-flip-hor"),
  flipver = document.getElementById("btn-flip-ver"),
  fingerImages = {
    " ": ["../img/manos/1p.png", "../img/manos/2p.png"],
    1: ["../img/manos/1m.png"],
    q: ["../img/manos/1m.png"],
    z: ["../img/manos/1m.png"],
    a: ["../img/manos/1m.png"],
    2: ["../img/manos/1a.png"],
    x: ["../img/manos/1a.png"],
    w: ["../img/manos/1a.png"],
    s: ["../img/manos/1a.png"],
    3: ["../img/manos/1med.png"],
    c: ["../img/manos/1med.png"],
    d: ["../img/manos/1med.png"],
    e: ["../img/manos/1med.png"],
    5: ["../img/manos/1i.png"],
    4: ["../img/manos/1i.png"],
    v: ["../img/manos/1i.png"],
    b: ["../img/manos/1i.png"],
    g: ["../img/manos/1i.png"],
    t: ["../img/manos/1i.png"],
    r: ["../img/manos/1i.png"],
    f: ["../img/manos/1i.png"],
    0: ["../img/manos/2m.png"],
    ñ: ["../img/manos/2m.png"],
    p: ["../img/manos/2m.png"],
    9: ["../img/manos/2a.png"],
    ".": ["../img/manos/2a.png"],
    l: ["../img/manos/2a.png"],
    o: ["../img/manos/2a.png"],
    8: ["../img/manos/2med.png"],
    ",": ["../img/manos/2med.png"],
    k: ["../img/manos/2med.png"],
    i: ["../img/manos/2med.png"],
    y: ["../img/manos/2i.png"],
    h: ["../img/manos/2i.png"],
    n: ["../img/manos/2i.png"],
    m: ["../img/manos/2i.png"],
    u: ["../img/manos/2i.png"],
    j: ["../img/manos/2i.png"],
    7: ["../img/manos/2i.png"],
    6: ["../img/manos/2i.png"],
  };

var timer,
  maxTime = 600,
  timeLeft = maxTime,
  charIndex = (mistakes = isTyping = 0),
  mainNav = document.getElementById("main-nav"),
  navbarToggle = document.getElementById("navbar-toggle"),
  container = document.getElementById("container"),
  delayinput = document.getElementById("inputValue"),
  btncontainer = document.getElementById("buttonContainer"),
  capturedImageElement = document.getElementById("capturedImage"),
  generatedpan = "",
  pc = null,
  dc = null,
  constraints = null,
  currentStream,
  canvas = document.createElement("canvas"),
  context = canvas.getContext("2d");

delayinput.onchange = function () {
  inpField.focus();
};

navbarToggle.addEventListener("click", function () {
  if (this.classList.contains("active")) {
    mainNav.style.display = "none";
    this.classList.remove("active");
  } else {
    mainNav.style.display = "flex";
    this.classList.add("active");
  }
});
fliphor.addEventListener("click", function () {
  inpField.focus();
  videoElement.classList.toggle("flipped-x");
  capturedImageElement.classList.toggle("flipped-x");
});

flipver.addEventListener("click", function () {
  inpField.focus();
  videoElement.classList.toggle("flipped-y");
  capturedImageElement.classList.toggle("flipped-y");
});

tryAgainBtn.addEventListener("click", reset);
videoSelect.onchange = function () {
  capturedImageElement.style.display = "none";
  videoElement.style.display = "block";
  inpField.focus();
  if (videoElement.srcObject) {
    // Close the previous stream
    videoElement.srcObject.getTracks().forEach((track) => track.stop());
  }
  localStorage.setItem("videoSource", videoSelect.value);
  captureWebcam();
};

function gotDevices(deviceInfos) {
  // Handles being called several times to update labels. Preserve values.
  const values = selectors.map((select) => select.value);
  selectors.forEach((select) => {
    while (select.firstChild) {
      select.removeChild(select.firstChild);
    }
  });
  for (let i = 0; i !== deviceInfos.length; ++i) {
    const deviceInfo = deviceInfos[i];
    const option = document.createElement("option");
    option.value = deviceInfo.deviceId;
    if (deviceInfo.kind === "videoinput") {
      option.text = deviceInfo.label || `camera ${videoSelect.length + 1}`;
      videoSelect.appendChild(option);
    }
  }
  selectors.forEach((select, selectorIndex) => {
    if (
      Array.prototype.slice
        .call(select.childNodes)
        .some((n) => n.value === values[selectorIndex])
    ) {
      select.value = values[selectorIndex];
    }
  });
  vs = localStorage.getItem("videoSource");
  if (vs) {
    videoSelect.value = vs;
  }
}

function gotStream(stream) {
  // Close the previous stream if exists
  if (videoElement.srcObject) {
    videoElement.srcObject.getTracks().forEach((track) => track.stop());
  }
  videoElement.srcObject = stream;
  btncontainer.style.display = "block";
  //videoElement.style.transform = "scaleX(-1)";
  // Refresh button list in case labels have become available
  return navigator.mediaDevices.enumerateDevices();
}

function handleError(error) {
  console.log(
    "navigator.MediaDevices.getUserMedia error: ",
    error.message,
    error.name
  );
}

function createPeerConnection() {
  var config = { sdpSemantics: "unified-plan" };
  config.iceServers = [
    {
      urls: ["stun:stun.l.google.com:19302"],
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
  return pc;
}

async function negotiate() {
  try {
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // wait for ICE gathering to complete
    await new Promise((resolve) => {
      if (pc.iceGatheringState === "complete") {
        resolve();
      } else {
        const checkState = () => {
          if (pc.iceGatheringState === "complete") {
            pc.removeEventListener("icegatheringstatechange", checkState);
            resolve();
          }
        };
        pc.addEventListener("icegatheringstatechange", checkState);
      }
    });

    const response = await fetch("/offer_cv", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sdp: pc.localDescription.sdp,
        type: pc.localDescription.type,
      }),
    });

    const answer = await response.json();
    await pc.setRemoteDescription(answer);
  } catch (e) {
    alert(e);
  }
}

async function start() {
  pc = createPeerConnection();
  dc = pc.createDataChannel("chat", { ordered: false });
  negotiate();
  dc.onclose = () => console.log("data channel closed");
  dc.onopen = function () {
    console.log("data channel created");
    captureWebcam();
    coordinate(0);
  };
}

function captureWebcam() {
  let vs = localStorage.getItem("videoSource");
  let constraints = {
    audio: false,
    video: {
      width: { min: 900, max: 1920 },
      height: { min: 700, max: 1080 },
    },
  };

  if (vs) {
    constraints.video.deviceId = vs;
  }
  if (constraints.video) {
    navigator.mediaDevices
      .getUserMedia(constraints)
      .then(gotStream)
      .then(gotDevices)
      .catch(handleError);
  }
}

async function coordinate(stat) {
  first = sessionStorage.getItem("first");
  let benchmark_coords = new Object(),
    practice_coords = new Object(),
    camera_coords = new Object(),
    user_params = new Object();
  user_params = await getuserParams();
  if (first === "true" && stat === 0) {
    alert(
      "Por favor escribe la oracion para que el sistema analice tu modo de escritura."
    );
    spinwrap.style.display = "none";
    inpField.style.display = "block";
    container.style.display = "flex";
    sessionStorage.setItem("first", "false");
    Object.assign(
      benchmark_coords,
      await loadParagraph(paragraphs[0]).then((res) => waitForKeyPress(res, 0))
    );
    stat = 1;
    sessionStorage.setItem(
      "benchmark_coords",
      JSON.stringify(benchmark_coords)
    );
  } else {
    stat = 1;
  }
  if (stat === 1) {
    alert(
      "Por favor escribe las siguientes oraciones con los dedos que se indican. \nEVITA HACERLO DEMASIADO RAPIDO"
    );
    hands.style.display = "flex";
    for (let index = 0; index < paragraphs.length; index++) {
      resp = await loadParagraph(paragraphs[index]).then((res) =>
        waitForKeyPress(res, 1)
      );
      Object.keys(resp).forEach((key) => {
        if(camera_coords[key] && camera_coords[key].length > 0){
          camera_coords[key] = resp[key].concat(camera_coords[key]);
        }else{
          camera_coords[key] = resp[key];
        }
      });
    }
    const bandera = {msg: 1};
    dc.send(JSON.stringify(bandera));
    console.log(await waitForMessage(dc, 1));
    console.log(camera_coords);
    stat = 2;
    sessionStorage.setItem("camera_coords", JSON.stringify(camera_coords));
  }
  if (stat === 2) {
    alert(
      "Practice. Escribe la oracion segun indique el dedo. \nEVITA HACERLO DEMASIADO RAPIDO"
    );
    if (Object.entries(benchmark_coords === 0)) {
      benchmark_coords = JSON.parse(sessionStorage.getItem("benchmark_coords"));
    }
    await loadParagraph(paragraphs[0]).then((res) => waitForKeyPress(res, 2));
    const bandera = {msg: 2};
    dc.send(JSON.stringify(bandera));
    /*
    try {
      const response = await fetch("/words/", {
        body: JSON.stringify({ letters: ["an", "es"], limit: 10 }),
        headers: { "Content-type": "application/json;charset=UTF-8" },
        method: "POST",
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
function GetImportantKeys(camera_coords, benchmark_coords, maxdistane) {
  const keysWithDiff = [];
  for (const key in camera_coords) {
    if (benchmark_coords.hasOwnProperty(key)) {
      const coords1 = camera_coords[key];
      const coords2 = benchmark_coords[key];
      distance = euclideanDistance(coords1, coords2);
      if (distance >= maxdistane) {
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

function showFinger(opt) {
  const spanElements = typingText.querySelectorAll("span");
  const charIndexOffset = opt ? 0 : 1;
  const charElement = spanElements[charIndex + charIndexOffset];
  if (!charElement) {
    return;
  }
  const cf = charElement.innerText.toLowerCase();
  const images = fingerImages[cf] || [];
  if (images[0].includes("1")) {
    iiElement.src = images[0] || "../img/manos/1.png";
    idElement.src = "../img/manos/2.png";
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
}

function resetSound() {
  audioElements.forEach((audioElement) => {
    audioElement.pause();
    audioElement.currentTime = 0;
  });
}

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
        playSound("sound-key");
      } else {
        mistakes++;
        characters[charIndex].classList.add("incorrect");
        playSound("sound-mistake");
      }
      charIndex++;
    }
    characters.forEach((span) => span.classList.remove("active"));
    if (charIndex < characters.length - 1) {
      characters[charIndex].classList.add("active");
    }
    let wpm = Math.round(
      ((charIndex - mistakes) / 5 / (maxTime - timeLeft)) * 60
    );
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
    let wpm = Math.round(
      ((charIndex - mistakes) / 5 / (maxTime - timeLeft)) * 60
    );
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
    let response = await fetch("/user/params", {
      headers: {
        Authorization: "Bearer " + window.sessionStorage.getItem("jwt"),
      },
    });
    let data = await handleErrors(response).json();
    return data;
  } catch (error) {
    console.error(error.message);
  }
}

function handleErrors(response) {
  if (!response.ok) {
    throw Error(response.status + " " + response.statusText);
  }
  return response;
}

function loadParagraph(sentence) {
  spinwrap.style.display = "none";
  inpField.style.display = "block";
  container.style.display = "flex";
  videoElement.style.display = "block";
  capturedImageElement.style.display = "none";
  return new Promise((resolve) => {
    typingText.innerHTML = "";
    sentence.split("").forEach((char) => {
      let span = `<span>${char}</span>`;
      typingText.innerHTML += span;
    });
    typingText.querySelectorAll("span")[0].classList.add("active");
    typingText.addEventListener("click", () => inpField.focus());
    resolve(sentence.length);
    showFinger(true);
  });
}

async function waitForKeyPress(len, status) {
  let fingecoords = {};
  const CHUNK_SIZE = 16 * 1024; // Chunk size in bytes
  let frameIndex = 0; // Index to track the current frame being sent
  let chunks = []; // Array to store the chunks of the current frame
  let characters = typingText.querySelectorAll("span");
  let error = false;
  let index = charIndex;
  //dc.onbufferedamountlow = sendNextChunk;
  return new Promise(async (resolve) => {
    const onKeyPress = async (event) => {
      const frame = await captureFrame();
      if (frame) {
        splitFrameIntoChunks(frame, CHUNK_SIZE, status, event.key);
        for (i = 0; i <= chunks.length; i++) {
          sendNextChunk();
        }
      }
      if (len >= 1) {
        showFinger(false);
      }
      initTyping(event.key);
      const msg = await waitForMessage(dc, event.key);
      if ("error" in msg) {
        error = true;
        while (
          characters[charIndex].innerText !== characters[index].innerText
        ) {
          characters[charIndex].classList = [];
          charIndex--;
        }
        if (characters[charIndex].classList.contains("incorrect")) {
          characters[charIndex].classList.replace("incorrect", "active");
        }
        if (characters[charIndex].classList.contains("correct")) {
          characters[charIndex].classList.replace("correct", "active");
        }
      } else {
        index++;
        error = false;
        agregarTecla(msg.key, msg.coords);
        len--;
        if (len === 0) {
          document.removeEventListener("keypress", onKeyPress);
          reset();
          resolve(fingecoords);
        }
      }
    };
    document.addEventListener("keypress", onKeyPress);
  });

  function sendNextChunk() {
    if (frameIndex >= chunks.length) {
      frameIndex = 0;
      chunks = [];
    } else {
      const chunk = chunks[frameIndex];
      dc.send(chunk);
      frameIndex++;
    }
  }

  function captureFrame() {
    return new Promise((resolve, reject) => {
      var video = videoElement;
      // Set the canvas dimensions to match the video dimensions
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      delay = delayinput.value;
      setTimeout(function () {
        // Draw the current video frame onto the canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        // Get the image data from the canvas
        var imageData = canvas.toDataURL("image/jpeg");
        capturedImageElement.src = imageData;
        capturedImageElement.style.display = "block";
        videoElement.style.display = "none";
        resolve(imageData);
      }, delay);
    });
  }

  function splitFrameIntoChunks(frame, CHUNK_SIZE, status, key) {
    const totalchunks = Math.ceil(frame.length / CHUNK_SIZE);
    for (let i = 0; i < totalchunks; i++) {
      const start = i * CHUNK_SIZE;
      const end = start + CHUNK_SIZE;
      const chunk = frame.slice(start, end);
      const chunkData = {
        chunk: chunk,
        totalchunks: totalchunks,
        status: status,
        key: key,
        index: charIndex,
      };
      const jsonChunk = JSON.stringify(chunkData);
      chunks.push(jsonChunk);
    }
  }

  // Agregar una tecla y sus coordenadas al objeto
  function agregarTecla(tecla, coordenadas) {
    if (fingecoords[tecla]) {
      fingecoords[tecla].push(coordenadas);
    } else {
      fingecoords[tecla] = [coordenadas];
    }
  }
}

function waitForMessage(dc, msgId) {
  return new Promise((resolve, reject) => {
    const handler = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.key === msgId) {
        //dc.removeEventListener("message", handler);
        console.log("llegue");
        resolve(msg);
      }else if (msg.msg === msgId){
        console.log("cacurnio");
        resolve(msg);
      }
    };

    dc.addEventListener("message", handler);
  });
}
