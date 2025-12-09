# PhoWhisper Server

Simple FastAPI server for vinai/PhoWhisper-base ASR with ffmpeg conversion, chunking, in-process inference queue and optional Cloudinary upload.

## Run locally
1. Install ffmpeg (system package).
2. python3 -m venv venv && source venv/bin/activate
3. pip install -r requirements.txt
4. export HF_MODEL_NAME="vinai/PhoWhisper-base"
5. uvicorn app.main:app --reload

## Deploy to Render
- Push repo to GitHub, create new Web Service on Render, set start command from Procfile.

## Env vars
- CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET (optional)
- HF_MODEL_NAME (default vinai/PhoWhisper-base)
- MAX_UPLOAD_MB (default 50)
- USE_GPU (1/0)
