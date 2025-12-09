# app/config.py
import os

# Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Hugging Face / Model
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "vinai/PhoWhisper-base")
HF_HOME = os.getenv("HF_HOME")  # optional

# # Limits
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

# # Inference control
USE_GPU = os.getenv("USE_GPU", "1") == "1"  # default try GPU
CHUNK_MS = int(os.getenv("CHUNK_MS", "30000"))
CHUNK_OVERLAP_MS = int(os.getenv("CHUNK_OVERLAP_MS", "1000"))
