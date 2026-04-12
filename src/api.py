"""
FastAPI Backend and App Mounting

This serves as the core API router for the TTS system, allowing it to be horizontally
scaled or accessed remotely via REST / WebSockets. It also mounts the Gradio application
so both the frontend and API can be served on the same port.
"""
import os
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import gradio as gr
import uvicorn
import wave
import io
from fastapi.responses import Response

from src.model import VibeVoiceTTS
from src.app import create_gradio_blocks

app = FastAPI(title="Vn-EmoVoice API")

# Setup CORS for mock deployments and frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
tts_model = VibeVoiceTTS(device="cpu") # use cpu for mock to avoid driver warnings

class TTSRequest(BaseModel):
    text: str
    speaker: str = "Female"
    topic: str = "Neutral Assistant"

@app.post("/api/generate")
async def generate_audio(request: TTSRequest):
    """
    REST endpoint to generate audio. Returns a WAV file.
    """
    sr, audio_data = tts_model.synthesize(request.text, request.speaker, request.topic)
    
    # Convert numpy array to WAV bytes
    byte_io = io.BytesIO()
    with wave.open(byte_io, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sr)
        wav_file.writeframes(audio_data.tobytes())
    
    return Response(content=byte_io.getvalue(), media_type="audio/wav")

@app.websocket("/api/stream")
async def stream_progress(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming of text chunking progress.
    The client sends the text, and the server yields progress updates.
    """
    await websocket.accept()
    data = await websocket.receive_text()
    
    # Send processing status based on chunking
    async for chunk in tts_model.stream_text_chunks(data):
        await websocket.send_text(chunk)
        
    await websocket.send_text("[DONE]")
    await websocket.close()

# Mount Gradio Frontend
print("[*] Mounting Gradio blocks...")
gradio_app = create_gradio_blocks(tts_model)
app = gr.mount_gradio_app(app, gradio_app, path="/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
