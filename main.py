from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import io
import soundfile as sf
from kokoro import KPipeline

app = FastAPI()
pipeline = KPipeline(lang_code="a")  # American English


@app.post("/tts")
async def tts(req: Request):
    data = await req.json()
    text = data["text"][:2000]

    # Generate speech (use first generator chunk)
    generator = pipeline(text, voice="af_heart")
    gs, ps, audio = next(generator)  # audio is a NumPy float array

    # Convert audio array to WAV bytes
    buffer = io.BytesIO()
    sf.write(buffer, audio, 24000, format="WAV")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="audio/wav")
