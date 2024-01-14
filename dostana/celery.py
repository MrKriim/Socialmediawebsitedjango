# dostana/celery.py
from celery import Celery
from celery import shared_task
from PIL import Image

app = Celery('dostana', broker='redis://localhost:6379/0')  # Update the broker URL accordingly

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Define your tasks directly in celery.py using shared_task
@shared_task
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
