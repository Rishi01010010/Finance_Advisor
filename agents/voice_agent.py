from fastapi import FastAPI, File, UploadFile
import whisper
import pyttsx3

app = FastAPI()
model = whisper.load_model("base")
tts_engine = pyttsx3.init()

@app.post("/stt")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_path = f"/tmp/{file.filename}"
    with open(audio_path, "wb") as f:
        f.write(await file.read())
    result = model.transcribe(audio_path)
    return {"transcription": result["text"]}

@app.post("/tts")
async def speak_text(text: str):
    audio_path = "/tmp/output_audio.mp3"
    tts_engine.save_to_file(text, audio_path)
    tts_engine.runAndWait()
    return {"audio_file": audio_path}