from copy import Error
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import io
import soundfile as sf
from kokoro import KPipeline
import numpy as np
import newspaper
import asyncio
import tempfile
import os
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("readtome")

app = FastAPI(title="ReadToMe", version="0.1.0")

MAX_CHARS = 30_000
SAMPLE_RATE = 24000
VOICE = "af_heart"

pipeline = KPipeline(lang_code="a")


def synthesize_to_wav_bytes(text: str, voice: Optional[str] = VOICE) -> bytes:
    """
    Synchronous function that runs the Kokoro pipeline and returns WAV bytes.
    We write to a temporary file to avoid huge memory spikes from concatenating arrays.
    """
    generator = pipeline(text, voice=voice)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        tmp_path = tmpfile.name

    try:
        audio_chunks = []
        for _, _, item in generator:
            logger.info(item)
            if isinstance(item, tuple) and len(item) >= 3:
                audio = item[2]
            else:
                audio = item
            if audio is None:
                continue
            audio_chunks.append(np.asarray(audio))

        if not audio_chunks:
            raise RuntimeError("No audio produced by TTS pipeline")

        full_audio = np.concatenate(audio_chunks)

        sf.write(tmp_path, full_audio, SAMPLE_RATE, format="WAV")
        with open(tmp_path, "rb") as f:
            data = f.read()
        return data
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


@app.post("/tts")
async def tts(req: Request):
    logger.info("received request")
    payload = await req.json()
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in JSON payload")

    article = newspaper.Article(url)
    try:
        article.download()
        article.parse()
    except Exception as e:
        logger.exception("Failed to download/parse article")
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch or parse article: {e}"
        )

    text = (article.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="No extractable text found at URL")

    if len(text) > MAX_CHARS:
        raise HTTPException(
            status_code=400,
            detail=f"Article too long ({len(text)} characters). Max allowed: {MAX_CHARS}",
        )

    try:
        wav_bytes = await asyncio.to_thread(synthesize_to_wav_bytes, text, VOICE)
    except Exception as e:
        logger.exception("TTS pipeline failed")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

    return StreamingResponse(io.BytesIO(wav_bytes), media_type="audio/wav")
