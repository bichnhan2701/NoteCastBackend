# app/main.py
import os, tempfile, time, shutil, asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from .audio_utils import to_wav_16k_mono, chunk_wav, cleanup_files, get_duration_ms
from .model import transcribe_chunk, get_asr
from .worker import inference_consumer, submit_job
from .config import MAX_UPLOAD_BYTES, CHUNK_MS, CHUNK_OVERLAP_MS, HF_MODEL_NAME
from .schemas import TranscriptionResponse
from typing import Optional

app = FastAPI(title="PhoWhisper ASR")

@app.on_event("startup")
async def startup_event():
    get_asr()
    asyncio.create_task(inference_consumer(transcribe_chunk))

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    file: Optional[UploadFile] = File(None),
    cloudinary_url: Optional[str] = Form(None),
    store_playback: bool = Form(False)
):
    if not file and not cloudinary_url:
        raise HTTPException(status_code=400, detail="Provide 'file' or 'cloudinary_url'")

    tmp_files = []
    try:
        if file:
            content = await file.read()
            if len(content) > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="File too large")
            tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
            tmp_in.write(content)
            tmp_in.flush()
            tmp_in.close()
            input_path = tmp_in.name
            tmp_files.append(input_path)
        else:
            import requests
            r = requests.get(cloudinary_url, stream=True, timeout=60)
            if r.status_code != 200:
                raise HTTPException(status_code=400, detail="Could not fetch cloudinary_url")
            tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".tmp")
            with open(tmp_in.name, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            input_path = tmp_in.name
            tmp_files.append(input_path)

        wav_path = to_wav_16k_mono(input_path)
        tmp_files.append(wav_path)

        duration_ms = get_duration_ms(wav_path)
        if duration_ms <= CHUNK_MS:
            chunks = [(wav_path, 0, int(duration_ms))]
        else:
            chunk_list = chunk_wav(wav_path, chunk_ms=CHUNK_MS, overlap_ms=CHUNK_OVERLAP_MS)
            chunks = chunk_list
            tmp_files.extend([c[0] for c in chunk_list])

        start_time = time.time()
        chunk_results = []
        for chunk_path, start_ms, end_ms in chunks:
            res = await submit_job(transcribe_chunk, chunk_path)
            text = res.get("text", "") if isinstance(res, dict) else str(res)
            chunk_results.append({
                "start": start_ms / 1000.0,
                "end": end_ms / 1000.0,
                "text": text
            })

        full_text = " ".join([c["text"] for c in chunk_results]).strip()
        processing_time = time.time() - start_time

        playback_url = None
        if store_playback:
            try:
                from .cloudinary_utils import upload_file_to_cloudinary
                playback_res = upload_file_to_cloudinary(wav_path)
                playback_url = playback_res.get("secure_url")
            except Exception:
                playback_url = None

        response = {
            "text": full_text,
            "duration_seconds": duration_ms / 1000.0,
            "model": HF_MODEL_NAME,
            "processing_time_seconds": processing_time,
            "chunks": chunk_results,
            "playback_url": playback_url
        }
        return JSONResponse(response)
    finally:
        cleanup_files(tmp_files)

# # Thêm route GET / để trả về thông báo khi truy cập root
# @app.get("/")
# def read_root():
#     return {"message": "PhoWhisper ASR server is running."}
