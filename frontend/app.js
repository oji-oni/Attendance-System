const API_URL = 'PASTE_YOUR_API_URL_HERE'; // From SAM outputs

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const statusDiv = document.getElementById('status');
const loader = document.getElementById('loader');

// Initialize Webcam
async function initWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
        video.srcObject = stream;
    } catch (err) {
        console.error("Webcam error:", err);
        showStatus("Webcam access denied", "error");
    }
}

async function capture(action) {
    statusDiv.style.display = 'none';
    loader.style.display = 'block';

    try {
        // 1. Capture Image
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9));

        // 2. Get Presigned URL
        const urlRes = await fetch(`${API_URL}upload-url?type=attendance&action=${action}`);
        const { url, key } = await urlRes.json();

        // 3. Upload to S3
        await fetch(url, {
            method: 'PUT',
            body: blob,
            headers: { 'Content-Type': 'image/jpeg' }
        });

        showStatus(`Processing ${action.toUpperCase()}... Success will be recorded shortly.`, "success");
        
        // Wait 3 seconds and reset (visual feedback)
        setTimeout(() => {
            statusDiv.style.display = 'none';
            loader.style.display = 'none';
        }, 3000);

    } catch (err) {
        console.error("Capture error:", err);
        showStatus("Failed to process attendance. Try again.", "error");
        loader.style.display = 'none';
    }
}

function showStatus(msg, type) {
    statusDiv.innerText = msg;
    statusDiv.className = `status-msg ${type}`;
    statusDiv.style.display = 'block';
}

initWebcam();
