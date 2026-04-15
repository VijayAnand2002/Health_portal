/**
 * WebRTC and WebSocket Signaling for Health Portal Consultation
 */

let localStream;
let peerConnection;
let socket;
let isScreenSharing = false;
let pendingIceCandidates = [];

// Media Elements
const localVideo = document.getElementById('local-video');
const remoteVideo = document.getElementById('remote-video');
const waitingPlaceholder = document.getElementById('waiting-placeholder');
const statusBadge = document.getElementById('connection-status');
const chatMessages = document.getElementById('chat-messages');
const cameraSelect = document.getElementById('camera-select');

// ICE Server Configuration (Public Google STUN servers)
const rtcConfig = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        { urls: 'stun:stun2.l.google.com:19302' }
    ],
    iceCandidatePoolSize: 10
};

/**
 * Device Enumeration
 */
async function populateCameraList() {
    if (!cameraSelect) return;

    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');

        cameraSelect.innerHTML = '';

        if (videoDevices.length === 0) {
            const option = document.createElement('option');
            option.value = "";
            option.text = "No cameras found";
            cameraSelect.appendChild(option);
            return;
        }

        videoDevices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.text = device.label || `Camera ${cameraSelect.length + 1}`;
            cameraSelect.appendChild(option);
        });

        // Event listener for camera change
        cameraSelect.onchange = () => {
            if (cameraSelect.value) {
                switchCamera(cameraSelect.value);
            }
        };

        console.log(`[Media] Listed ${videoDevices.length} video devices`);
    } catch (err) {
        console.error("Error enumerating devices:", err);
    }
}

async function switchCamera(deviceId) {
    if (!localStream) return;

    try {
        console.log(`[Media] Switching to camera: ${deviceId}`);

        // Stop current video tracks
        localStream.getVideoTracks().forEach(track => track.stop());

        // Get new constraints
        const constraints = {
            video: { deviceId: { exact: deviceId } },
            audio: true // Keep audio
        };

        const newStream = await navigator.mediaDevices.getUserMedia(constraints);
        const newVideoTrack = newStream.getVideoTracks()[0];

        // Replace track in local stream object (for UI updates)
        const oldVideoTrack = localStream.getVideoTracks()[0];
        localStream.removeTrack(oldVideoTrack);
        localStream.addTrack(newVideoTrack);

        // Update local video element
        localVideo.srcObject = localStream;

        // Replace track in RTCPeerConnection (if active)
        if (peerConnection) {
            const sender = peerConnection.getSenders().find(s => s.track && s.track.kind === 'video');
            if (sender) {
                console.log("[WebRTC] Replacing track in active P2P session");
                await sender.replaceTrack(newVideoTrack);
            }
        }

        console.log("[Media] Camera switch successful");
    } catch (err) {
        console.error("Error switching camera:", err);
        alert("Could not switch to the selected camera. It might be in use.");
        // Try to revert or re-populate
        populateCameraList();
    }
}

/**
 * Initialize Media and Socket
 */
async function init() {
    try {
        console.log("Starting WebRTC session initialization...");
        updateStatus('Requesting Media...', 'warning', true);

        // Simplified constraints for maximum compatibility
        const constraints = {
            video: true,
            audio: true
        };

        console.log("Calling getUserMedia with:", constraints);
        localStream = await navigator.mediaDevices.getUserMedia(constraints);
        console.log("Media stream acquired successfully");

        // Now that we have permission, labels will be available
        await populateCameraList();

        localVideo.srcObject = localStream;
        localVideo.onloadedmetadata = () => {
            console.log("Local video metadata loaded, playing...");
            localVideo.play().catch(e => console.error("Local video auto-play blocked:", e));
        };

        updateStatus('Connecting to Signal...', 'warning', true);
        initWebSocket();
    } catch (err) {
        console.error('CRITICAL: Media acquisition failed:', err);
        let errorMsg = 'Could not access camera/microphone.';
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            errorMsg = 'Permission denied. Please check your browser settings and refresh.';
        } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
            errorMsg = 'No camera or microphone found.';
        } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
            errorMsg = 'Camera/Mic is already in use by another application.';
        }

        alert(errorMsg);
        updateStatus('Hardware Error', 'danger');
    }
}

/**
 * Set up WebSocket signaling
 */
function initWebSocket() {
    console.log("Connecting to WebSocket:", WS_URL);
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        console.log('Signaling server connected. Identity:', IS_DOCTOR ? 'Doctor' : 'Patient');
        updateStatus('Waiting for Participant', 'info', false);

        // Probe for existing users
        sendSignal({ type: 'user-presence-probe' });
    };

    socket.onmessage = async (e) => {
        try {
            const data = JSON.parse(e.data);
            console.log(`[Signaling] Incoming: ${data.type || 'unknown'} from ${data.sender_id || 'system'}`);

            switch (data.type) {
                case 'offer':
                    console.log('%c[WebRTC] Received Offer', 'color: #007bff; font-weight: bold');
                    await handleOffer(data.offer);
                    break;
                case 'answer':
                    console.log('%c[WebRTC] Received Answer', 'color: #28a745; font-weight: bold');
                    await handleAnswer(data.answer);
                    break;
                case 'ice-candidate':
                    console.log('[WebRTC] Received Remote ICE Candidate');
                    await handleNewICECandidate(data.candidate);
                    break;
                case 'user-joined':
                    console.log(`[Sync] User Joined: ${data.username} (Role: ${data.role}, ID: ${data.user_id})`);
                    if (data.user_id === parseInt(USER_ID)) {
                        console.warn("[Sync] Ignore self-join notification");
                        return;
                    }

                    // Reply with presence to let the newcomer know we are here
                    sendSignal({ type: 'user-presence', username: USER_NAME, role: IS_DOCTOR ? 'doctor' : 'patient' });

                    if (IS_DOCTOR && data.role === 'patient') {
                        console.log('[Sync] Doctor detected Patient joining. Initiating call...');
                        initiateCall();
                    }
                    break;
                case 'user-presence-probe':
                    console.log('[Sync] Responding to presence probe');
                    sendSignal({ type: 'user-presence', username: USER_NAME, role: IS_DOCTOR ? 'doctor' : 'patient' });
                    break;
                case 'user-presence':
                    console.log(`[Sync] Presence confirmed: ${data.username} (${data.role})`);
                    if (IS_DOCTOR && data.role === 'patient') {
                        console.log('[Sync] Patient presence detected. Initiating call...');
                        initiateCall();
                    }
                    break;
                case 'chat':
                    appendMessage(data.user, data.message, 'received');
                    break;
                case 'user-left':
                    console.log('[Sync] Participant left the room');
                    updateStatus('Participant Left', 'warning');
                    remoteVideo.srcObject = null;
                    waitingPlaceholder.style.display = 'flex';
                    if (peerConnection) {
                        peerConnection.close();
                        peerConnection = null;
                    }
                    break;
                default:
                    console.log('[Signaling] Unhandled message type:', data.type);
            }
        } catch (err) {
            console.error('[Signaling] Error processing message:', err);
        }
    };

    socket.onclose = (e) => {
        console.warn('WebSocket signaling lost:', e.code, e.reason);
        updateStatus('Offline (Signaling Lost)', 'danger');
        // Critical: Don't auto-reload here as it might loop, but alert if unexpected
    };

    socket.onerror = (err) => {
        console.error('WebSocket Error:', err);
        updateStatus('Signaling Error', 'danger');
    };
}

/**
 * Create Peer Connection
 */
function createPeerConnection() {
    if (peerConnection) return;

    console.log("Initializing RTCPeerConnection...");
    peerConnection = new RTCPeerConnection(rtcConfig);

    // Add local tracks to peer connection
    localStream.getTracks().forEach(track => {
        console.log(`Adding track: ${track.kind}`);
        peerConnection.addTrack(track, localStream);
    });

    // Handle remote tracks
    peerConnection.ontrack = (event) => {
        console.log("Remote track received. Stream count:", event.streams.length);
        if (remoteVideo.srcObject !== event.streams[0]) {
            remoteVideo.srcObject = event.streams[0];
            remoteVideo.onloadedmetadata = () => {
                console.log("Remote video metadata loaded, playing...");
                remoteVideo.play().catch(e => console.error("Remote video play failed:", e));
            };
            waitingPlaceholder.style.display = 'none';
            updateStatus('Consultation Active', 'success', false);
        }
    };

    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            console.log(`[WebRTC] Local ICE Candidate: ${event.candidate.candidate.substring(0, 50)}...`);
            sendSignal({
                type: 'ice-candidate',
                candidate: event.candidate
            });
        } else {
            console.log("[WebRTC] All local ICE candidates gathered");
        }
    };

    peerConnection.oniceconnectionstatechange = () => {
        console.log(`%c[WebRTC] ICE Connection State: ${peerConnection.iceConnectionState}`, 'color: #ffc107; font-weight: bold');
        if (peerConnection.iceConnectionState === 'failed') {
            console.error("[WebRTC] ICE Negotiation failed. Check STUN/TURN server connectivity.");
            updateStatus('Connection Failed', 'danger', true);
        }
    };

    peerConnection.onconnectionstatechange = () => {
        const state = peerConnection.connectionState;
        console.log(`%c[WebRTC] Peer Connection State: ${state}`, 'color: #17a2b8; font-weight: bold');

        switch (state) {
            case 'connected':
                console.log("%c[WebRTC] P2P Session Established!", 'color: #28a745; font-size: 1.1rem; font-weight: bold');
                updateStatus('P2P Encrypted', 'success', false);
                break;
            case 'disconnected':
                console.warn("[WebRTC] Peer disconnected temporarily");
                updateStatus('Reconnecting...', 'warning', true);
                break;
            case 'failed':
                console.error("[WebRTC] Peer connection failed permanently");
                updateStatus('Connection Lost', 'danger', true);
                break;
            case 'closed':
                console.log("[WebRTC] Peer connection closed");
                break;
        }
    };
}

/**
 * Signaling Handlers
 */
async function initiateCall() {
    if (peerConnection) return;

    console.log("Building SDP Offer...");
    createPeerConnection();

    try {
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        console.log("Local description set (Offer)");

        sendSignal({
            type: 'offer',
            offer: offer
        });
    } catch (e) {
        console.error("Failed to initiate call:", e);
    }
}

async function handleOffer(offer) {
    console.log("Processing remote offer...");
    createPeerConnection();

    try {
        await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
        console.log("Remote description set (Offer)");

        // Drain buffered candidates
        while (pendingIceCandidates.length > 0) {
            const candidate = pendingIceCandidates.shift();
            await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
        }

        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);
        console.log("Local description set (Answer)");

        sendSignal({
            type: 'answer',
            answer: answer
        });
    } catch (e) {
        console.error("Error handling offer:", e);
    }
}

async function handleAnswer(answer) {
    if (!peerConnection) return;

    try {
        console.log("Processing remote answer...");
        await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
        console.log("Remote description set (Answer)");

        while (pendingIceCandidates.length > 0) {
            const candidate = pendingIceCandidates.shift();
            await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
        }
    } catch (e) {
        console.error("Error setting remote answer:", e);
    }
}

async function handleNewICECandidate(candidate) {
    if (peerConnection && peerConnection.remoteDescription) {
        try {
            await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
        } catch (e) {
            console.error('Failed to add remote ICE candidate:', e);
        }
    } else {
        console.log("Buffering remote ICE candidate...");
        pendingIceCandidates.push(candidate);
    }
}

function sendSignal(data) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
    } else {
        console.warn("Signal dropped (WebSocket not connected):", data.type);
    }
}

/**
 * UI Controls
 */
function toggleAudio() {
    const audioTrack = localStream.getAudioTracks()[0];
    if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        console.log(`Audio ${audioTrack.enabled ? 'Enabled' : 'Muted'}`);
        const btn = document.querySelector('[title="Toggle Mic"]');
        btn.classList.toggle('active');
        const icon = document.getElementById('mic-icon');
        icon.className = audioTrack.enabled ? 'bi bi-mic-fill' : 'bi bi-mic-mute-fill';
    }
}

function toggleVideo() {
    const videoTrack = localStream.getVideoTracks()[0];
    if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        console.log(`Video ${videoTrack.enabled ? 'Enabled' : 'Stopped'}`);
        const btn = document.querySelector('[title="Toggle Video"]');
        btn.classList.toggle('active');
        const icon = document.getElementById('video-icon');
        icon.className = videoTrack.enabled ? 'bi bi-camera-video-fill' : 'bi bi-camera-video-off-fill';
    }
}

async function toggleScreenShare() {
    if (!peerConnection) return;

    try {
        if (!isScreenSharing) {
            console.log("Requesting screen capture...");
            const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
            const videoTrack = screenStream.getVideoTracks()[0];

            // Swap video track in peer connection
            const sender = peerConnection.getSenders().find(s => s.track && s.track.kind === 'video');
            if (sender) {
                console.log("Switching P2P track to screen share");
                sender.replaceTrack(videoTrack);
            }

            videoTrack.onended = () => {
                console.log("Screen share ended by system");
                if (isScreenSharing) toggleScreenShare(); // Revert back
            };

            isScreenSharing = true;
        } else {
            console.log("Reverting to camera...");
            const videoTrack = localStream.getVideoTracks()[0];
            const sender = peerConnection.getSenders().find(s => s.track && s.track.kind === 'video');
            if (sender) {
                sender.replaceTrack(videoTrack);
            }
            isScreenSharing = false;
        }
        document.querySelector('[title="Share Screen"]').classList.toggle('active');
    } catch (err) {
        console.error("Screen share failed:", err);
    }
}

function updateStatus(text, colorClass, isPulse = false) {
    if (!statusBadge) return;
    statusBadge.className = `badge bg-${colorClass} rounded-pill px-3 py-2 shadow-sm mb-2`;
    let icon = 'bi-circle-fill';
    if (colorClass === 'success') icon = 'bi-shield-lock-fill';
    if (colorClass === 'warning') icon = 'bi-broadcast';
    if (colorClass === 'danger') icon = 'bi-exclamation-triangle-fill';

    statusBadge.innerHTML = `<i class="bi ${icon} me-2 ${isPulse ? 'pulse' : ''}"></i>${text}`;
}

/**
 * Chat Logic
 */
function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (message) {
        sendSignal({
            type: 'chat',
            message: message,
            user: USER_NAME
        });
        appendMessage('You', message, 'sent');
        input.value = '';
    }
}

function appendMessage(user, text, type) {
    if (!chatMessages) return;
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${type} shadow-sm small italic`;
    msgDiv.innerHTML = `<strong>${user}:</strong> ${text}`;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Global scope initialization
init();
