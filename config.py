import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
CLEANUP_INTERVAL_SECONDS = 600  # 10 minutes
FILE_MAX_AGE_SECONDS = 3600  # 1 hour
