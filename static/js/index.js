"use strict";
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
  notifications = document.querySelector(".notifications"),
  fingerImages = {
    " ": ["../static/img/manos/1p.png", "../static/img/manos/2p.png"],
    1: ["../static/img/manos/1m.png"],
    q: ["../static/img/manos/1m.png"],
    z: ["../static/img/manos/1m.png"],
    a: ["../static/img/manos/1m.png"],
    2: ["../static/img/manos/1a.png"],
    x: ["../static/img/manos/1a.png"],
    w: ["../static/img/manos/1a.png"],
    s: ["../static/img/manos/1a.png"],
    3: ["../static/img/manos/1med.png"],
    c: ["../static/img/manos/1med.png"],
    d: ["../static/img/manos/1med.png"],
    e: ["../static/img/manos/1med.png"],
    5: ["../static/img/manos/1i.png"],
    4: ["../static/img/manos/1i.png"],
    v: ["../static/img/manos/1i.png"],
    b: ["../static/img/manos/1i.png"],
    g: ["../static/img/manos/1i.png"],
    t: ["../static/img/manos/1i.png"],
    r: ["../static/img/manos/1i.png"],
    f: ["../static/img/manos/1i.png"],
    0: ["../static/img/manos/2m.png"],
    ñ: ["../static/img/manos/2m.png"],
    p: ["../static/img/manos/2m.png"],
    9: ["../static/img/manos/2a.png"],
    ".": ["../static/img/manos/2a.png"],
    l: ["../static/img/manos/2a.png"],
    o: ["../static/img/manos/2a.png"],
    8: ["../static/img/manos/2med.png"],
    ",": ["../static/img/manos/2med.png"],
    k: ["../static/img/manos/2med.png"],
    i: ["../static/img/manos/2med.png"],
    y: ["../static/img/manos/2i.png"],
    h: ["../static/img/manos/2i.png"],
    n: ["../static/img/manos/2i.png"],
    m: ["../static/img/manos/2i.png"],
    u: ["../static/img/manos/2i.png"],
    j: ["../static/img/manos/2i.png"],
    7: ["../static/img/manos/2i.png"],
    6: ["../static/img/manos/2i.png"],
  };

var timer,
  maxTime = 600,
  timeLeft = maxTime,
  charIndex = 0,
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
  context = canvas.getContext("2d"),
  testData = [],
  cameraData = [];

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
  let vs = localStorage.getItem("videoSource");
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
  dc = pc.createDataChannel("chat", { ordered: true });
  negotiate();
  dc.onclose = () => console.log("data channel closed");
  dc.onerror = function (event) {
    console.error("Error en el canal de datos: ", event.error);
  };
  dc.onopen = function () {
    console.log("data channel created");
    captureWebcam();
    coordinate(0);
  };
}

function captureWebcam() {
  const vs = localStorage.getItem("videoSource");
  let constraints = {
    audio: false,
    video: {
      width: { min: 300, max: 1920 },
      height: { min: 200, max: 1080 },
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
  if (stat === 0) {
    alert(
      "Por favor escribe las siguientes oraciones con los dedos que se indican. \nEVITA HACERLO DEMASIADO RAPIDO"
    );
    hands.style.display = "flex";
    for (let index = 0; index < 3; index++) {
      let sentence = await loadParagraph(
        paragraphs[Math.floor(Math.random() * paragraphs.length)]
      );
      let resp = await TypeText(sentence, 0);
      cameraData.push(...resp);
    }
    console.log(JSON.stringify(cameraData));
    dc.send(JSON.stringify({ programPhase: 2, cameraData }));
    stat = 1;
    sessionStorage.setItem("cameraData", JSON.stringify(cameraData));
  }
  if (stat === 1) {
    createToast(
      "info",
      "Comencemos practicando los siguientes ejercicios.",
      4000
    );
    let dd = [];
    let dataretreived = "";
    if (dataretreived === "") {
      let phrases = [];
      let sentence = await loadParagraph(
        paragraphs[Math.floor(Math.random() * paragraphs.length)]
      );
      let resp = await TypeText(sentence, 1);
      testData.push(...resp);
      testData.forEach((element) => {
        if (element["coords"] !== null) {
          cameraData.push(element);
        }
      });
      resp.forEach((element) => {
        if (element["coords"] !== null) {
          dd.push(element);
        }
      });
      console.log("este es dd: ", JSON.stringify(dd));
      dc.send(JSON.stringify({ programPhase: 2, cameraData: dd }));
      dd = [];
      loadSpinner(true);
      try {
        const response = await fetch("/words/", {
          body: JSON.stringify(testData),
          headers: { "Content-type": "application/json;charset=UTF-8" },
          method: "POST",
        });
        const data = await handleErrors(response).json();
        phrases = data.oraciones;
      } catch (error) {
        console.error(error.message);
      }
      loadSpinner(false);
      for (let index = 0; index < phrases.length; index++) {
        let sentence = await loadParagraph(phrases[index]);
        let resp = await TypeText(sentence, 1);
        testData.push(...resp);
      }
      
      coordinate(1);
    } else {
    }
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

function showFinger(key) {
  const images = fingerImages[key] || [];
  const iiDefaultSrc = "../static/img/manos/1.png";
  const idDefaultSrc = "../static/img/manos/2.png";

  if (images.length > 0) {
    const firstImage = images[0] || iiDefaultSrc;

    if (firstImage.includes("1")) {
      iiElement.src = firstImage;
      idElement.src = idDefaultSrc;
    } else {
      iiElement.src = iiDefaultSrc;
      idElement.src = firstImage;
    }
  } else {
    iiElement.src = iiDefaultSrc;
    idElement.src = idDefaultSrc;
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
  let iskeywrong = false;
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
        iskeywrong = false;
      } else {
        mistakes++;
        characters[charIndex].classList.add("incorrect");
        playSound("sound-mistake");
        iskeywrong = true;
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
  return iskeywrong;
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
    resolve(sentence);
  });
}

async function TypeText(sentence, programPhase) {
  inpField.focus();
  let correctKeys = [];
  const CHUNK_SIZE = Math.min(pc.sctp.maxMessageSize, 262144) - 100; //tamaño del chunk menos 100 bytes debido a la serializacion
  let keyIndex = 0; // Index to track the current frame being sent
  let chunks = []; // Array to store the chunks of the current frame
  let characters = typingText.querySelectorAll("span");
  let error = false;
  dc.bufferedAmountLowThreshold = CHUNK_SIZE;
  dc.addEventListener("bufferedamountlow", sendChunks);
  dc.onmessage = (e) => {
    messageReceived(e.data);
  };
  tryAgainBtn.addEventListener("click", reset);
  showFinger(sentence[0]);
  return new Promise(async (resolve) => {
    const onKeyPress = async (event) => {
      let key = event.key;
      let frame = await captureFrame();
      let keyTime = Date.now();
      if (error === false) {
        if (key === sentence[keyIndex]) {
          characters[keyIndex].classList.add("correct");
          characters[keyIndex].classList.remove("active");
          playSound("sound-key");
          if (isalfa(key)) {
            chunks = chunks.concat(
              splitFrameIntoChunks(
                frame,
                CHUNK_SIZE,
                programPhase,
                key,
                keyTime,
                keyIndex
              )
            ); //chunks de la tecla presionada
            sendChunks();
          }
        } else if (programPhase !== 0) {
          // Fase de test, si hay error se marca
          correctKeys.push({
            key: sentence[keyIndex],
            coords: null,
            time: keyTime,
          });
          characters[keyIndex].classList.add("incorrect");
          characters[keyIndex].classList.remove("active");
          playSound("sound-mistake");
        } else {
          //Fase de camara, si hay error se regresa
          playSound("sound-mistake");
          createToast("error", "Tecla incorrecta", 2000);
          keyIndex--;
        }
        if (characters.length - 1 == keyIndex) {
          //fin de la escritura
          keyIndex = 0;
          document.removeEventListener("keypress", onKeyPress);
          await new Promise((r) => setTimeout(r, 1000)); //espera 1s a que se obtenga el resultado
          resolve(correctKeys);
        } else {
          keyIndex++;
          showFinger(sentence[keyIndex]);
          characters[keyIndex].classList.add("active");
        }
      }
    };

    document.addEventListener("keypress", onKeyPress);
  });

  function sendChunks() {
    while (chunks.length !== 0) {
      if (dc.bufferedAmount >= CHUNK_SIZE) {
        break;
      }
      let ch = chunks.shift();
      dc.send(JSON.stringify(ch));
    }
  }

  function captureFrame() {
    return new Promise((resolve, reject) => {
      let video = videoElement;
      let delay = delayinput.value;
      // Set the canvas dimensions to match the video dimensions
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
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

  function splitFrameIntoChunks(
    frame,
    CHUNK_SIZE,
    programPhase,
    key,
    keyTime,
    keyIndex
  ) {
    let totalchunks = Math.ceil(frame.length / CHUNK_SIZE);
    let keyChunks = [];
    for (let i = 0; i < totalchunks; i++) {
      let start = i * CHUNK_SIZE;
      let end = start + CHUNK_SIZE;
      let frameChunk = frame.slice(start, end);
      let chunkData = {
        keyIndex: keyIndex,
        frameChunk: frameChunk,
        programPhase: programPhase,
        key: key,
        keyTime: keyTime,
        isLast:
          i < totalchunks - 1 ? false : i === totalchunks - 1 ? true : false,
      };
      keyChunks.push(chunkData);
    }
    return keyChunks;
  }

  function messageReceived(data) {
    let jsonData = JSON.parse(data);
    let dataIndex = jsonData["keyIndex"];
    if ("error" in jsonData) {
      playSound("sound-mistake");
      error = true;
      createToast("error", jsonData["error"], 2000);
      chunks = [];
      for (let i = dataIndex; i <= keyIndex; i++) {
        characters[i].classList = [];
      }
      keyIndex = dataIndex;
      characters[keyIndex].classList.add("active");
      setTimeout(function () {
        error = false;
      }, 500);
    } else {
      correctKeys.push(jsonData);
    }
    showFinger(sentence[keyIndex]);
  }

  function reset() {
    keyIndex = 0;
    for (let i = 0; i <= characters.length - 1; i++) {
      characters[i].classList = [];
    }
    characters[0].classList.add("active");
    correctKeys = [];
  }
}

const toastDetails = {
  timer: 2000,
  success: {
    icon: "fa-circle-check",
  },
  error: {
    icon: "fa-circle-xmark",
  },
  warning: {
    icon: "fa-triangle-exclamation",
  },
  info: {
    icon: "fa-circle-info",
  },
};

const removeToast = (toast) => {
  toast.classList.add("hide");
  if (toast.timeoutId) clearTimeout(toast.timeoutId); // Clearing the timeout for the toast
  setTimeout(() => toast.remove(), 2000); // Removing the toast after 500ms
};

const createToast = (id, text, time) => {
  // Getting the icon and text for the toast based on the id passed
  const icon = toastDetails[id];
  const toast = document.createElement("li"); // Creating a new 'li' element for the toast
  toast.className = `toast ${id}`; // Setting the classes for the toast
  // Setting the inner HTML for the toast
  toast.innerHTML = `<div class="column">
                       <i class="fa-solid ${icon.icon}"></i>
                       <span>${text}</span>
                    </div>
                    <i class="fa-solid fa-xmark" onclick="removeToast(this.parentElement)"></i>`;
  notifications.appendChild(toast); // Append the toast to the notification ul
  // Setting a timeout to remove the toast after the specified duration
  toast.timeoutId = setTimeout(() => removeToast(toast), time);
};

function loadSpinner(load) {
  if (load === true) {
    spinwrap.style.display = "flex";
    inpField.style.display = "none";
    container.style.display = "none";
  } else {
    spinwrap.style.display = "none";
    inpField.style.display = "block";
    container.style.display = "flex";
  }
}

function isalfa(cr) {
  return /^[A-Za-záéíóúÁÉÍÓÚñÑ]$/.test(cr);
}
