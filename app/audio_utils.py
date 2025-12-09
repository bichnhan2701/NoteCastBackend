# app/audio_utils.py
import subprocess, uuid, os, tempfile
from pydub import AudioSegment
from typing import List, Tuple

def to_wav_16k_mono(input_path: str, out_dir=None) -> str:
    if out_dir is None:
        out_dir = tempfile.gettempdir()
    out_path = os.path.join(out_dir, f"{uuid.uuid4().hex}.wav")
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ac", "1", "-ar", "16000", "-sample_fmt", "s16",
        out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path

def get_duration_ms(wav_path: str) -> float:
    audio = AudioSegment.from_wav(wav_path)
    return len(audio)

def chunk_wav(wav_path: str, chunk_ms: int=30000, overlap_ms: int=1000, out_dir=None) -> List[Tuple[str,int,int]]:
    if out_dir is None:
        out_dir = tempfile.gettempdir()
    audio = AudioSegment.from_wav(wav_path)
    duration_ms = len(audio)
    chunks = []
    start = 0
    while start < duration_ms:
        end = min(start + chunk_ms, duration_ms)
        chunk = audio[start:end]
        chunk_path = os.path.join(out_dir, f"{uuid.uuid4().hex}.wav")
        chunk.export(chunk_path, format="wav")
        chunks.append((chunk_path, start, end))
        start = end - overlap_ms
    return chunks

def cleanup_files(paths):
    for p in paths:
        try:
            os.remove(p)
        except Exception:
            pass
