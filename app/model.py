# app/model.py
from transformers import pipeline
import torch
from .config import HF_MODEL_NAME

_asr = None

def get_asr():
    global _asr
    if _asr is None:
        device = 0 if torch.cuda.is_available() else -1
        _asr = pipeline("automatic-speech-recognition", model=HF_MODEL_NAME, device=device)
    return _asr

def transcribe_chunk(wav_path: str):
    pipe = get_asr()
    result = pipe(wav_path)
    return result
