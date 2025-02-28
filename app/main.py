import httpx
import tempfile
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
 
load_dotenv()
 
app = FastAPI()
 
@app.get("/", response_class=HTMLResponse)
async def index():
    """
    Serve the main HTML page which contains:
      - A local audio visualizer (blue waveform)
      - A remote audio visualizer (red waveform)
      - A transcription display area
      - JavaScript that sets up a WebRTC connection, records remote audio, and posts it to the transcription endpoint
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Real-Time Voice App with Transcription</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
          .visualizer {
              width: 100%;
              height: 150px;
              background-color: #f5f5f5;
              border: 1px solid #ddd;
              margin-bottom: 20px;
          }
          #transcription {
              border: 1px solid #ddd;
              padding: 10px;
              background-color: #f9f9f9;
              height: 150px;
              overflow-y: auto;
          }
      </style>
    </head>
    <body class="p-3">
      <div class="container">
          <h1 class="mb-4">Real-Time Voice App with Transcription</h1>
          <div class="mb-3">
              <p><strong>Local Input (Blue):</strong></p>
              <canvas id="localVisualizer" class="visualizer"></canvas>
          </div>
          <div class="mb-3">
              <p><strong>Remote Audio Visualization (Red):</strong></p>
              <canvas id="backendVisualizer" class="visualizer"></canvas>
          </div>
          <div class="mb-3">
              <p><strong>Transcription:</strong></p>
              <div id="transcription"></div>
          </div>
      </div>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
      <script>
        async function init() {
          try {
            // 1. Get ephemeral key from the server
            const tokenResponse = await fetch("/session");
            const tokenData = await tokenResponse.json();
            const EPHEMERAL_KEY = tokenData.client_secret.value;
            console.log("Ephemeral key received:", EPHEMERAL_KEY);
           
            // 2. Create a new RTCPeerConnection
            const pc = new RTCPeerConnection();
            const audioEl = document.createElement("audio");
            audioEl.autoplay = true;
            document.body.appendChild(audioEl);
            let transcriptionStarted = false;
           
            // 3. When a remote track is received…
            pc.ontrack = e => {
              if (e.streams && e.streams[0]) {
                audioEl.srcObject = e.streams[0];
                startBackendVisualizer(e.streams[0]);
                // Start transcription only once
                if (!transcriptionStarted) {
                  transcriptionStarted = true;
                  recordAndTranscribe(e.streams[0]);
                }
              }
            };
           
            // 4. Get the microphone stream and add it to the connection
            const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            pc.addTrack(micStream.getTracks()[0]);
            startLocalVisualizer(micStream);
           
            // 5. Create a data channel (for events) if needed
            const dc = pc.createDataChannel("oai-events");
            dc.addEventListener("message", (e) => {
              console.log("Data Channel message:", e.data);
            });
           
            // 6. Create an SDP offer
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            console.log("SDP offer created and set as local description.");
           
            // 7. Send the SDP offer to the OpenAI realtime API
            const baseUrl = "https://api.openai.com/v1/realtime";
            const model = "gpt-4o-mini-realtime-preview-2024-12-17";
            const sdpResponse = await fetch(`${baseUrl}?model=${model}`, {
              method: "POST",
              body: offer.sdp,
              headers: {
                Authorization: `Bearer ${EPHEMERAL_KEY}`,
                "Content-Type": "application/sdp"
              },
            });
           
            // 8. Set the remote description with the answer
            const answer = {
              type: "answer",
              sdp: await sdpResponse.text(),
            };
            await pc.setRemoteDescription(answer);
            console.log("SDP answer received and set as remote description. WebRTC connection established.");
          } catch (error) {
            console.error("Error initializing WebRTC connection:", error);
          }
        }
       
        function startLocalVisualizer(stream) {
          const localCanvas = document.getElementById('localVisualizer');
          const localCtx = localCanvas.getContext('2d');
          localCanvas.width = localCanvas.offsetWidth;
          localCanvas.height = localCanvas.offsetHeight;
          const audioContext = new (window.AudioContext || window.webkitAudioContext)();
          const analyser = audioContext.createAnalyser();
          analyser.fftSize = 2048;
          const bufferLength = analyser.frequencyBinCount;
          const dataArray = new Uint8Array(bufferLength);
          const source = audioContext.createMediaStreamSource(stream);
          source.connect(analyser);
          function draw() {
            requestAnimationFrame(draw);
            analyser.getByteTimeDomainData(dataArray);
            localCtx.fillStyle = '#f5f5f5';
            localCtx.fillRect(0, 0, localCanvas.width, localCanvas.height);
            localCtx.lineWidth = 2;
            localCtx.strokeStyle = '#007bff';
            localCtx.beginPath();
            const sliceWidth = localCanvas.width / dataArray.length;
            let x = 0;
            for (let i = 0; i < dataArray.length; i++) {
              const v = dataArray[i] / 128.0;
              const y = v * localCanvas.height / 2;
              if (i === 0) {
                localCtx.moveTo(x, y);
              } else {
                localCtx.lineTo(x, y);
              }
              x += sliceWidth;
            }
            localCtx.lineTo(localCanvas.width, localCanvas.height / 2);
            localCtx.stroke();
          }
          draw();
        }
       
        function startBackendVisualizer(stream) {
          const backendCanvas = document.getElementById('backendVisualizer');
          const backendCtx = backendCanvas.getContext('2d');
          backendCanvas.width = backendCanvas.offsetWidth;
          backendCanvas.height = backendCanvas.offsetHeight;
          const audioContext = new (window.AudioContext || window.webkitAudioContext)();
          const analyser = audioContext.createAnalyser();
          analyser.fftSize = 2048;
          const bufferLength = analyser.frequencyBinCount;
          const dataArray = new Uint8Array(bufferLength);
          const source = audioContext.createMediaStreamSource(stream);
          source.connect(analyser);
          function draw() {
            requestAnimationFrame(draw);
            analyser.getByteTimeDomainData(dataArray);
            backendCtx.fillStyle = '#f5f5f5';
            backendCtx.fillRect(0, 0, backendCanvas.width, backendCanvas.height);
            backendCtx.lineWidth = 2;
            backendCtx.strokeStyle = '#ff0000';
            backendCtx.beginPath();
            const sliceWidth = backendCanvas.width / dataArray.length;
            let x = 0;
            for (let i = 0; i < dataArray.length; i++) {
              const v = dataArray[i] / 128.0;
              const y = v * backendCanvas.height / 2;
              if (i === 0) {
                backendCtx.moveTo(x, y);
              } else {
                backendCtx.lineTo(x, y);
              }
              x += sliceWidth;
            }
            backendCtx.lineTo(backendCanvas.width, backendCanvas.height / 2);
            backendCtx.stroke();
          }
          draw();
        }
       
        // Record the remote audio in 5-second chunks, send to /transcribe, and display the result
        function recordAndTranscribe(stream) {
          let options = { mimeType: 'audio/webm' };
          let mediaRecorder = new MediaRecorder(stream, options);
          let chunks = [];
         
          mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
              chunks.push(e.data);
            }
          };
         
          mediaRecorder.onstop = () => {
            let blob = new Blob(chunks, { type: 'audio/webm' });
            chunks = [];
            let formData = new FormData();
            formData.append('file', blob, 'audio.webm');
           
            fetch('/transcribe', {
              method: 'POST',
              body: formData
            })
            .then(response => response.json())
            .then(data => {
              console.log("Transcription:", data);
              let transcriptionDiv = document.getElementById("transcription");
              transcriptionDiv.innerText += data.text + "\\n";
              // Continue recording after transcription
              recordAndTranscribe(stream);
            })
            .catch(error => {
              console.error("Error transcribing audio:", error);
              // Retry recording even if an error occurs
              recordAndTranscribe(stream);
            });
          };
         
          mediaRecorder.start();
          setTimeout(() => {
            if (mediaRecorder.state === "recording") {
              mediaRecorder.stop();
            }
          }, 5000); // record for 5 seconds
        }
       
        init();
      </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
 
@app.get("/session")
async def session_endpoint():
    """
    Create an ephemeral session by sending a POST request to the OpenAI realtime API.
    Returns:
      - A JSON object containing session details, including a client secret used for authentication.
    """
   
    openai_api_key = "*****"
    if not openai_api_key:
        return JSONResponse(status_code=500, content={"error": "OPENAI_API_KEY not set"})
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/realtime/sessions",
            headers={
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini-realtime-preview-2024-12-17",
                "voice": "verse",
                "instructions": "You are a helpful assistant and only respond in English even if the user asks you questions in other languages.If user speak in other language please ask them to speak in English only"
               
            },
        )
    print("Response Text:", response.text)
    data = response.json()
    print("Response JSON:", data)
    return JSONResponse(content=data)
 
SYSTEM_PROMPT = "Transcribe the audio and produce output exclusively in English."
 
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Endpoint to transcribe an uploaded audio file.
    Reads the uploaded file, saves it temporarily, sends it to OpenAI's Whisper API,
    and returns the transcription result.
   
    Args:
      file (UploadFile): The uploaded audio file in opus format.
   
    Returns:
      JSONResponse: The JSON response containing the transcription text.
    """
    openai_api_key = "*****"
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
   
    contents = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".opus", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
   
    url = "https://api.openai.com/v1/audio/transcriptions"
    with open(tmp_path, "rb") as f:
        files = {
            "file": (file.filename, f, file.content_type),
        }
        data_payload = {
            "model": "whisper-1",
            "prompt": SYSTEM_PROMPT,
            "language": "en"
        }
        async with httpx.AsyncClient() as client:
            transcription_response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {openai_api_key}"
                },
                data=data_payload,
                files=files
            )
    os.remove(tmp_path)
   
    if transcription_response.status_code != 200:
        raise HTTPException(status_code=transcription_response.status_code, detail=transcription_response.text)
    transcription_data = transcription_response.json()
    return JSONResponse(content=transcription_data)
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8116)