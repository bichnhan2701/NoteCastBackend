# app/audio_utils.py
# app/audio_utils.py
import subprocess
import os
import uuid
import tempfile
from typing import List, Tuple

# You can set FFMPEG_BIN/FFPROBE_BIN env vars if you bundle ffmpeg static binaries
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")
FFPROBE_BIN = os.getenv("FFPROBE_BIN", "ffprobe")

def to_wav_16k_mono(input_path: str, out_dir=None) -> str:
    """
    Convert any input audio to WAV PCM16, 16kHz, mono using ffmpeg subprocess.
    Returns path to converted wav. Raises CalledProcessError if ffmpeg not found or fails.
    """
    if out_dir is None:
        out_dir = tempfile.gettempdir()
    out_path = os.path.join(out_dir, f"{uuid.uuid4().hex}.wav")
    cmd = [
        FFMPEG_BIN, "-y", "-i", input_path,
        "-ac", "1", "-ar", "16000", "-sample_fmt", "s16",
        out_path
    ]
    subprocess.run(cmd, check=True)
    return out_path

def get_duration_ms(file_path: str) -> float:
    """
    Use ffprobe to get duration in milliseconds.
    """
    cmd = [
        FFPROBE_BIN, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    output = subprocess.check_output(cmd)
    duration_s = float(output.strip())
    return duration_s * 1000.0

def chunk_wav(wav_path: str, chunk_ms: int=30000, overlap_ms: int=1000, out_dir=None) -> List[Tuple[str,int,int]]:
    """
    Create chunks by calling ffmpeg seeking (-ss) and -t for duration.
    Returns list of tuples (chunk_path, start_ms, end_ms).
    """
    if out_dir is None:
        out_dir = tempfile.gettempdir()
    duration_ms = int(get_duration_ms(wav_path))
    chunks = []
    start_ms = 0
    while start_ms < duration_ms:
        # compute end
        end_ms = min(start_ms + chunk_ms, duration_ms)
        if end_ms <= start_ms:
            break  # Không cắt nếu không còn dữ liệu

        out_path = os.path.join(out_dir, f"{uuid.uuid4().hex}.wav")
        # ffmpeg uses seconds
        start_s = start_ms / 1000.0
        dur_s = (end_ms - start_ms) / 1000.0
        cmd = [
            FFMPEG_BIN, "-y",
            "-i", wav_path,
            "-ss", str(start_s),
            "-t", str(dur_s),
            "-ac", "1", "-ar", "16000", "-sample_fmt", "s16",
            out_path
        ]
        subprocess.run(cmd, check=True)
        chunks.append((out_path, start_ms, end_ms))
        start_ms = end_ms - overlap_ms
    return chunks

def cleanup_files(paths):
    for p in paths:
        try:
            os.remove(p)
        except Exception:
            pass
