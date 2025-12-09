# app/cloudinary_utils.py
import cloudinary
import cloudinary.uploader
from .config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

def init_cloudinary():
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )

def upload_file_to_cloudinary(file_path: str, folder: str="phowhisper/raw"):
    init_cloudinary()
    res = cloudinary.uploader.upload(file_path, resource_type="auto", folder=folder)
    return res
