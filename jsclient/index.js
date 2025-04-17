// // Getting Elements from DOM
// const joinButton = document.getElementById("joinBtn");
// const leaveButton = document.getElementById("leaveBtn");
// const toggleMicButton = document.getElementById("toggleMicBtn");
// const toggleWebCamButton = document.getElementById("toggleWebCamBtn");
// const createButton = document.getElementById("createMeetingBtn");
// const videoContainer = document.getElementById("videoContainer");
// const textDiv = document.getElementById("textDiv");

// // Declare Variables
// let meeting = null;
// let meetingId = "";
// let isMicOn = false;
// let isWebCamOn = false;

// const inviteAI = async () => {
//     token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlrZXkiOiI1OWFlZDJlOS1lOGExLTQ5NWEtOWE1NC04NGFhM2EwOGVjM2IiLCJwZXJtaXNzaW9ucyI6WyJhbGxvd19qb2luIl0sImlhdCI6MTc0NDczMTY5OSwiZXhwIjoxNzQ3MzIzNjk5fQ.vj8c8zbSzbk6wesuy3_oeAc5o-0w6ZtIastp25Ya6ck";
//     try {
//       const response = await fetch("http://localhost:8000/join-player", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
        
//         body: JSON.stringify({ meeting_id: meetingId, token }),
//       });

//       if (!response.ok) throw new Error("Failed to invite AI");

//       console.log("AI Translator joined successfully");
      
//     } catch (error) {
//       console.log("Failed to invite AI Translator");
//       console.error("Error inviting AI:", error);
//     }
//   };

// function initializeMeeting() {
//     window.VideoSDK.config(TOKEN);
  
//     meeting = window.VideoSDK.initMeeting({
//       meetingId: meetingId, // required
//       name: "Thomas Edison", // required
//       micEnabled: true, // optional, default: true
//       webcamEnabled: false, // optional, default: true

//     });
  
//     meeting.join();

  
//     // Creating local participant
//     // createLocalParticipant();
  
//     // Setting local participant stream
//     meeting.localParticipant.on("stream-enabled", (stream) => {
//       setTrack(stream, null, meeting.localParticipant, true);
//     });
  
//     // meeting joined event
//     meeting.on("meeting-joined", () => {
//       textDiv.style.display = "none";
//       document.getElementById("grid-screen").style.display = "block";
//       document.getElementById(
//         "meetingIdHeading"
//       ).textContent = `Meeting Id: ${meetingId}`;
//     });
  
//     // meeting left event
//     meeting.on("meeting-left", () => {
//       videoContainer.innerHTML = "";
//     });
  
//     // Remote participants Event
//     // participant joined
//     meeting.on("participant-joined", (participant) => {
//         let videoElement = createVideoElement(
//           participant.id,
//           participant.displayName
//         );
//         let audioElement = createAudioElement(participant.id);
//         // stream-enabled
//         participant.on("stream-enabled", (stream) => {
//           setTrack(stream, audioElement, participant, false);
//         });
//         // videoContainer.appendChild(videoElement);
//         console.log(audioElement)
//         videoContainer.appendChild(audioElement);
//       });
    
//       // participants left
//       meeting.on("participant-left", (participant) => {
//         let vElement = document.getElementById(`f-${participant.id}`);
//         vElement.remove(vElement);
    
//         let aElement = document.getElementById(`a-${participant.id}`);
//         aElement.remove(aElement);
//       });
//   }



// // function createVideoElement() {}

// function createAudioElement(pId) {
//     let audioElement = document.createElement("audio");
//     audioElement.setAttribute("autoPlay", "false");
//     audioElement.setAttribute("playsInline", "true");
//     audioElement.setAttribute("controls", "false");
//     audioElement.setAttribute("id", `a-${pId}`);
//     audioElement.style.display = "none";
//     return audioElement;
//   }
  
//   // creating local participant
//   function createLocalParticipant() {
//     let localParticipant = createVideoElement(
//       meeting.localParticipant.id,
//       meeting.localParticipant.displayName
//     );
//     videoContainer.appendChild(localParticipant);
//   }
  
//   // setting media track
//   function setTrack(stream, audioElement, participant, isLocal) {
//     if (stream.kind == "video") {
//       isWebCamOn = true;
//       const mediaStream = new MediaStream();
//       mediaStream.addTrack(stream.track);
//       let videoElm = document.getElementById(`v-${participant.id}`);
//       videoElm.srcObject = mediaStream;
//       videoElm
//         .play()
//         .catch((error) =>
//           console.error("videoElem.current.play() failed", error)
//         );
//     }
//     if (stream.kind == "audio") {
//       if (isLocal) {
//         isMicOn = true;
//       } else {
//         const mediaStream = new MediaStream();
//         mediaStream.addTrack(stream.track);
//         audioElement.srcObject = mediaStream;
//         audioElement
//           .play()
//           .catch((error) => console.error("audioElem.play() failed", error));
//       }
//     }
//   }

// // Join Meeting Button Event Listener
// joinButton.addEventListener("click", async () => {
//   document.getElementById("join-screen").style.display = "none";
//   textDiv.textContent = "Joining the meeting...";

//   roomId = document.getElementById("meetingIdTxt").value;
//   meetingId = roomId;

//   initializeMeeting();
//   setTimeout(() => {
//     inviteAI();
//   }, 1000); 
// });

// // Create Meeting Button Event Listener
// createButton.addEventListener("click", async () => {
//   document.getElementById("join-screen").style.display = "none";
//   textDiv.textContent = "Please wait, we are joining the meeting";

//   // API call to create meeting
//   const url = `https://api.videosdk.live/v2/rooms`;
//   const options = {
//     method: "POST",
//     headers: { Authorization: TOKEN, "Content-Type": "application/json" },
//   };

//   const { roomId } = await fetch(url, options)
//     .then((response) => response.json())
//     .catch((error) => alert("error", error));
//   meetingId = roomId;

//   initializeMeeting();
  
// });




// Getting Elements from DOM
const joinButton = document.getElementById("joinBtn");
const leaveButton = document.getElementById("leaveBtn");
const toggleMicButton = document.getElementById("toggleMicBtn");
const toggleWebCamButton = document.getElementById("toggleWebCamBtn");
const createButton = document.getElementById("createMeetingBtn");
const videoContainer = document.getElementById("videoContainer");
const textDiv = document.getElementById("textDiv");

// Declare Variables
let meeting = null;
let meetingId = "";
let isMicOn = false;
let isWebCamOn = false;
let audioStreamMap = {}; // Store audio streams by participant ID

const inviteAI = async () => {
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlrZXkiOiI1OWFlZDJlOS1lOGExLTQ5NWEtOWE1NC04NGFhM2EwOGVjM2IiLCJwZXJtaXNzaW9ucyI6WyJhbGxvd19qb2luIl0sImlhdCI6MTc0NDczMTY5OSwiZXhwIjoxNzQ3MzIzNjk5fQ.vj8c8zbSzbk6wesuy3_oeAc5o-0w6ZtIastp25Ya6ck";
    try {
      const response = await fetch("http://localhost:8000/join-player", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        
        body: JSON.stringify({ meeting_id: meetingId, token }),
      });

      if (!response.ok) throw new Error("Failed to invite AI");

      console.log("AI Translator joined successfully");
      
    } catch (error) {
      console.log("Failed to invite AI Translator");
      console.error("Error inviting AI:", error);
    }
  };

function initializeMeeting() {
    window.VideoSDK.config(TOKEN);
  
    meeting = window.VideoSDK.initMeeting({
      meetingId: meetingId, // required
      name: "Thomas Edison", // required
      micEnabled: true, // optional, default: true
      webcamEnabled: false, // optional, default: true
      
    });
  
    meeting.join();

  
    // Creating local participant
    createLocalParticipant();
  
    // Setting local participant stream
    meeting.localParticipant.on("stream-enabled", (stream) => {
      setTrack(stream, null, meeting.localParticipant, true);
    });
  
    // meeting joined event
    meeting.on("meeting-joined", () => {
      textDiv.style.display = "none";
      document.getElementById("grid-screen").style.display = "block";
      document.getElementById(
        "meetingIdHeading"
      ).textContent = `Meeting Id: ${meetingId}`;
    });
  
    // meeting left event
    meeting.on("meeting-left", () => {
      videoContainer.innerHTML = "";
      // Clean up audio streams
      for (const streamId in audioStreamMap) {
        const stream = audioStreamMap[streamId];
        if (stream && stream.mediaStream) {
          stream.mediaStream.getTracks().forEach(track => track.stop());
        }
      }
      audioStreamMap = {};
    });
  
    // Remote participants Event
    // participant joined
    meeting.on("participant-joined", (participant) => {
        console.log("Participant joined:", participant.displayName);
        
        // Create video element for the participant
        let videoElement = createVideoElement(
          participant.id,
          participant.displayName
        );
        videoContainer.appendChild(videoElement);
        
        // Create audio element with controls for debugging
        let audioElement = createAudioElement(participant.id);
        videoContainer.appendChild(audioElement);
        
        // Check if this is the AI participant by name (adjust as needed)
        const isAIParticipant = participant.displayName.includes("AI") || 
                                participant.displayName.includes("Assistant") || 
                                participant.displayName.toLowerCase().includes("translator");
        
        // Track when the participant starts or stops speaking
        let isSpeaking = false;
        let speakingTimeout = null;

        // stream-enabled
        participant.on("stream-enabled", (stream) => {
          console.log(`Stream enabled: ${stream.kind} from ${participant.displayName}`);
          
          if (stream.kind === "audio") {
            // Initialize or update audio stream entry
            if (!audioStreamMap[participant.id]) {
              audioStreamMap[participant.id] = {
                mediaStream: null,
                isActive: false,
                lastActive: Date.now(),
                isAI: isAIParticipant
              };
            }
          }
          
          setTrack(stream, audioElement, participant, false, isAIParticipant);
        });

        // Handle stream updates
        participant.on("stream-updated", (stream) => {
          if (stream.kind === "audio") {
            console.log(`Stream updated: ${stream.kind} from ${participant.displayName}`);
            
            // Reset audio if needed when the stream is updated
            if (audioStreamMap[participant.id]) {
              audioStreamMap[participant.id].lastActive = Date.now();
            }
            
            setTrack(stream, audioElement, participant, false, isAIParticipant);
          }
        });
        
        // Handle stream disabled
        participant.on("stream-disabled", (stream) => {
          if (stream.kind === "audio" && audioStreamMap[participant.id]) {
            console.log(`Stream disabled: ${stream.kind} from ${participant.displayName}`);
            
            // Mark as inactive
            audioStreamMap[participant.id].isActive = false;
            
            // Stop audio tracks
            if (audioStreamMap[participant.id].mediaStream) {
              audioStreamMap[participant.id].mediaStream.getTracks().forEach(track => track.stop());
              audioStreamMap[participant.id].mediaStream = null;
            }
          }
        });
      });
    
      // participants left
      meeting.on("participant-left", (participant) => {
        console.log("Participant left:", participant.displayName);
        let vElement = document.getElementById(`f-${participant.id}`);
        if (vElement) vElement.remove();
    
        let aElement = document.getElementById(`a-${participant.id}`);
        if (aElement) aElement.remove();
        
        // Clean up audio stream for this participant
        if (audioStreamMap[participant.id]) {
          if (audioStreamMap[participant.id].mediaStream) {
            audioStreamMap[participant.id].mediaStream.getTracks().forEach(track => track.stop());
          }
          delete audioStreamMap[participant.id];
        }
      });
}

function createVideoElement(pId, displayName) {
  let videoFrame = document.createElement("div");
  videoFrame.setAttribute("id", `f-${pId}`);
  videoFrame.classList.add("video-frame");
  
  let nameTag = document.createElement("div");
  nameTag.classList.add("name-tag");
  nameTag.innerHTML = displayName;
  
  let videoElement = document.createElement("video");
  videoElement.classList.add("video-element");
  videoElement.setAttribute("id", `v-${pId}`);
  videoElement.setAttribute("playsinline", true);
  
  videoFrame.appendChild(videoElement);
  videoFrame.appendChild(nameTag);
  
  return videoFrame;
}

function createAudioElement(pId) {
    let audioElement = document.createElement("audio");
    audioElement.setAttribute("autoplay", "true");
    audioElement.setAttribute("playsinline", "true");
    audioElement.setAttribute("id", `a-${pId}`);
    
    // For debugging purposes - add controls to see audio elements
    audioElement.setAttribute("controls", "true");
    audioElement.style.display = "block";
    audioElement.style.height = "30px";
    audioElement.style.marginTop = "5px";
    
    return audioElement;
}
  
// creating local participant
function createLocalParticipant() {
  let localParticipant = createVideoElement(
    meeting.localParticipant.id,
    meeting.localParticipant.displayName
  );
  videoContainer.appendChild(localParticipant);
}
  
// Handle audio activity
function handleAudioActivity(participantId, isActive) {
  if (!audioStreamMap[participantId]) return;
  
  const currentTime = Date.now();
  const timeSinceLastActive = currentTime - audioStreamMap[participantId].lastActive;
  
  if (isActive) {
    // If this participant is active, pause other participants' audio
    audioStreamMap[participantId].isActive = true;
    audioStreamMap[participantId].lastActive = currentTime;
    
    // If it's the AI participant starting to speak, pause other audio
    if (audioStreamMap[participantId].isAI) {
      for (const id in audioStreamMap) {
        if (id !== participantId && audioStreamMap[id].isActive) {
          const audioEl = document.getElementById(`a-${id}`);
          if (audioEl && !audioEl.paused) {
            console.log(`Pausing audio from participant ${id} because AI is speaking`);
            audioEl.pause();
            audioStreamMap[id].isActive = false;
          }
        }
      }
    }
    // If it's a human participant starting to speak, pause AI audio
    else {
      for (const id in audioStreamMap) {
        if (audioStreamMap[id].isAI && audioStreamMap[id].isActive) {
          const audioEl = document.getElementById(`a-${id}`);
          if (audioEl && !audioEl.paused) {
            console.log(`Pausing AI audio because participant ${participantId} is speaking`);
            audioEl.pause();
            audioStreamMap[id].isActive = false;
          }
        }
      }
    }
  } else {
    // Mark this participant as inactive
    audioStreamMap[participantId].isActive = false;
  }
}

// setting media track
function setTrack(stream, audioElement, participant, isLocal, isAI = false) {
  if (stream.kind == "video") {
    isWebCamOn = true;
    const mediaStream = new MediaStream();
    mediaStream.addTrack(stream.track);
    let videoElm = document.getElementById(`v-${participant.id}`);
    if (videoElm) {
      videoElm.srcObject = mediaStream;
      videoElm
        .play()
        .catch((error) =>
          console.error("videoElem.current.play() failed", error)
        );
    }
  }
  if (stream.kind == "audio") {
    if (isLocal) {
      isMicOn = true;
    } else {
      // Stop any existing tracks for this participant
      if (audioStreamMap[participant.id] && audioStreamMap[participant.id].mediaStream) {
        audioStreamMap[participant.id].mediaStream.getTracks().forEach(track => {
          track.stop();
        });
      }
      
      // Create new media stream
      const mediaStream = new MediaStream();
      mediaStream.addTrack(stream.track);
      
      // Store media stream reference
      if (audioStreamMap[participant.id]) {
        audioStreamMap[participant.id].mediaStream = mediaStream;
        audioStreamMap[participant.id].isActive = true;
        audioStreamMap[participant.id].lastActive = Date.now();
        audioStreamMap[participant.id].isAI = isAI;
      }
      
      // Make sure audio element exists
      if (!audioElement) {
        audioElement = document.getElementById(`a-${participant.id}`);
        if (!audioElement) {
          console.error("Audio element not found for participant:", participant.id);
          return;
        }
      }
      
      // Always update the audio element with the new stream
      audioElement.srcObject = mediaStream;
      
      // Set volume to 1 (maximum) for AI participant
      if (isAI) {
        audioElement.volume = 1.0;
      }
      
      // Check if we should play this audio or not
      let shouldPlay = true;
      
      // AI should only play if no human is speaking
      if (isAI) {
        for (const id in audioStreamMap) {
          if (id !== participant.id && !audioStreamMap[id].isAI && audioStreamMap[id].isActive) {
            shouldPlay = false;
            console.log("Not playing AI audio because a human is speaking");
            break;
          }
        }
      } 
      // Human should pause AI audio
      else {
        for (const id in audioStreamMap) {
          if (audioStreamMap[id].isAI && audioStreamMap[id].isActive) {
            const aiAudioEl = document.getElementById(`a-${id}`);
            if (aiAudioEl && !aiAudioEl.paused) {
              console.log("Pausing AI audio because human started speaking");
              aiAudioEl.pause();
              audioStreamMap[id].isActive = false;
            }
          }
        }
      }
      
      // Force play audio only if it should play
      audioElement.muted = false;
      if (shouldPlay) {
        handleAudioActivity(participant.id, true);
        const playPromise = audioElement.play();
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              console.log(`Audio playing for participant: ${participant.displayName}`);
            })
            .catch((error) => {
              console.error(`Audio play failed for ${participant.displayName}:`, error);
              
              // Try to recover by adding a user interaction listener
              document.addEventListener('click', function audioUnlock() {
                audioElement.play()
                  .then(() => {
                    console.log("Audio unlocked after user interaction");
                    handleAudioActivity(participant.id, true);
                  })
                  .catch(e => console.error("Still couldn't play audio:", e));
                document.removeEventListener('click', audioUnlock);
              }, { once: true });
            });
        }
      } else {
        console.log(`Not playing audio for ${participant.displayName} because another participant is active`);
      }
      
      // Set up event listeners for audio tracking
      audioElement.onpause = () => {
        console.log(`Audio paused for participant: ${participant.displayName}`);
        handleAudioActivity(participant.id, false);
      };
      
      audioElement.onplay = () => {
        console.log(`Audio playing for participant: ${participant.displayName}`);
        handleAudioActivity(participant.id, true);
      };
      
      audioElement.onended = () => {
        console.log(`Audio ended for participant: ${participant.displayName}`);
        handleAudioActivity(participant.id, false);
      };
    }
  }
}

// Leave button event listener
leaveButton.addEventListener("click", () => {
  meeting.leave();
  document.getElementById("grid-screen").style.display = "none";
  document.getElementById("join-screen").style.display = "flex";
});

// Toggle mic button event listener
toggleMicButton.addEventListener("click", () => {
  if (isMicOn) {
    meeting.muteMic();
    toggleMicButton.textContent = "Unmute Mic";
  } else {
    meeting.unmuteMic();
    toggleMicButton.textContent = "Mute Mic";
  }
  isMicOn = !isMicOn;
});

// Join Meeting Button Event Listener
joinButton.addEventListener("click", async () => {
  document.getElementById("join-screen").style.display = "none";
  textDiv.textContent = "Joining the meeting...";
  textDiv.style.display = "block";

  roomId = document.getElementById("meetingIdTxt").value;
  meetingId = roomId;

  initializeMeeting();
  setTimeout(() => {
    inviteAI();
  }, 1000); 
});

// Create Meeting Button Event Listener
createButton.addEventListener("click", async () => {
  document.getElementById("join-screen").style.display = "none";
  textDiv.textContent = "Please wait, we are joining the meeting";
  textDiv.style.display = "block";

  // API call to create meeting
  const url = `https://api.videosdk.live/v2/rooms`;
  const options = {
    method: "POST",
    headers: { Authorization: TOKEN, "Content-Type": "application/json" },
  };

  const { roomId } = await fetch(url, options)
    .then((response) => response.json())
    .catch((error) => alert("error", error));
  meetingId = roomId;

  initializeMeeting();
  
  setTimeout(() => {
    inviteAI();
  }, 1000);
});