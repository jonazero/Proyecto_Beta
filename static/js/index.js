const videoElement = document.querySelector('video');
const videoSelect = document.querySelector('select#videoSource');
const selectors = [videoSelect];

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
      urls: "stun:openrelay.metered.ca:80",
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
  if (window.stream) {
    window.stream.getTracks().forEach(track => {
      track.stop();
    });
  }
  pc = createPeerConnection();

  dc = pc.createDataChannel('chat');
  dc.onclose = function () {
    console.log("data channel closed");
  }
  dc.onopen = function () {
    console.log("data channel created");
  };
  dc.onmessage = function (evt) {
    alert(evt.data)
  };
  const videoSource = videoSelect.value;
  const constraints = {
    video: { deviceId: videoSource ? { exact: videoSource } : undefined }
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
videoSelect.onchange = start;
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
