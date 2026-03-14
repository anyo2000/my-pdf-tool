import os
import uuid
import time
import threading
from config import UPLOAD_FOLDER, OUTPUT_FOLDER, FILE_MAX_AGE_SECONDS, CLEANUP_INTERVAL_SECONDS


def ensure_dirs():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def unique_filename(original_name, folder=None):
    if folder is None:
        folder = UPLOAD_FOLDER
    name, ext = os.path.splitext(original_name)
    unique = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    return os.path.join(folder, unique)


def validate_pdf(file_storage):
    if not file_storage or file_storage.filename == '':
        raise ValueError("파일이 선택되지 않았습니다.")
    if not file_storage.filename.lower().endswith('.pdf'):
        raise ValueError("PDF 파일만 업로드할 수 있습니다.")
    return True


def save_upload(file_storage, folder=None):
    if folder is None:
        folder = UPLOAD_FOLDER
    path = unique_filename(file_storage.filename, folder)
    file_storage.save(path)
    return path


def cleanup_old_files():
    now = time.time()
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if os.path.isfile(fpath):
                age = now - os.path.getmtime(fpath)
                if age > FILE_MAX_AGE_SECONDS:
                    try:
                        os.remove(fpath)
                    except OSError:
                        pass


def start_cleanup_thread():
    def loop():
        while True:
            time.sleep(CLEANUP_INTERVAL_SECONDS)
            cleanup_old_files()

    t = threading.Thread(target=loop, daemon=True)
    t.start()


def safe_remove(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
