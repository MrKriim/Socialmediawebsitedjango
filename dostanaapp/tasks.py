# tasks.py
from celery import Celery
from PIL import Image
import os

app = Celery('dostana')

@app.task
def process_uploaded_photo(photo_path):
    try:
        # Open the image using Pillow
        with Image.open(photo_path) as img:
            # Resize the image to a fixed size (e.g., 300x300)
            resized_img = img.resize((300, 300))

            # Save the resized image back to the original path
            resized_img.save(photo_path)
    except Exception as e:
        # Handle any exceptions that may occur during image processing
        print(f"Error processing photo {photo_path}: {e}")
