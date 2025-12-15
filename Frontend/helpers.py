import uuid
import base64
import os
import pickle
import dotenv
import traceback
from werkzeug import datastructures as ds
import logging
import requests
from flask import jsonify, Response

# ------------------ Load ENV Variables ------------------ #
# dotenv.load_dotenv()      -> Should Ideally be loaded via app.py

_baseUrl=os.getenv('base_url')
BACKEND_URL = f'{_baseUrl}:{os.getenv("backend_port")}'
print("Backend URL:", BACKEND_URL)
del _baseUrl

_cwd = os.path.abspath(os.getcwd())
UPLOADS_DIR:str = os.getenv("uploads_dir", r"Data\Uploads")
UPLOADS_DIR = os.path.join(_cwd, UPLOADS_DIR)
os.makedirs(UPLOADS_DIR, exist_ok=True) # Makes directory if not present.

# -------------------------------------------------------- #

def addFileMapping(_uuid, filename) -> bool:
    try:
        mapping_file = os.path.join(UPLOADS_DIR, 'mapping.pkl')
        print("Mapping", mapping_file)
        try:
            with open(mapping_file, 'rb') as mapp:
                mapping = pickle.load(mapp)
        except FileNotFoundError:
            mapping = {}
        mapping[_uuid] = filename
        
        with open(mapping_file, 'wb') as mapp:
            pickle.dump(mapping, mapp, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(e)
        # logging.exception("Unhandled", e)
        # traceback.print_exc
        return False
    
    return True

def saveFileToUploads(_uuid: str, file: ds.FileStorage) -> bool:
    try:
        filename = str(file.filename)
        _, ext = os.path.splitext(filename)
        filename_uuid = f'{_uuid}{ext}'
        file.save(os.path.join(UPLOADS_DIR, filename_uuid))
    
    except Exception as e:
        return False
    return True

def generate_uuid() -> str:
    """
    Generates a URL-safe Base64-encoded UUID (22 characters long).
    """
    # 1. Generate a UUID (128-bit)
    random_uuid = uuid.uuid4()
    
    # 2. Get the 16-byte binary representation (digest)
    # This removes the hyphens and represents the full 128 bits
    uuid_bytes = random_uuid.bytes
    
    # 3. Encode the 16 bytes using URL-safe Base64
    # The URL-safe variant replaces '+' with '-' and '/' with '_'
    encoded_bytes = base64.urlsafe_b64encode(uuid_bytes)
    
    # 4. Convert to a string and strip the trailing padding ('==')
    # A 16-byte input results in 22 characters plus '==' padding,
    # which is redundant for file names.
    base64_uuid = encoded_bytes.decode('utf-8').rstrip('==')
    
    return base64_uuid.replace('-', '0')
    
def backend_informFileUpload(_uuid: str, original_filename: str) -> bool:
    # Send a put request to backend
    # Informs backend that a new file has been uploaded with uuid
    response = requests.put(
        f'{BACKEND_URL}/file-saved',
        params={'_uuid': _uuid, 'filename': original_filename}
    )
    if response.status_code != 200:
        return False
    return True
    
def removeFile(file: str):
    filepath = os.path.join(UPLOADS_DIR, file)
    os.remove(filepath)

def getImageList():
    # Read mapping.pkl for list of files
    # Generate map: -> {uuid: uuid, fileName: filename}
    # return json
    mapping_file_path = os.path.join(UPLOADS_DIR, 'mapping.pkl')
    try:
        with open(mapping_file_path, 'rb') as mapp:
            mapping = pickle.load(mapp)
        return mapping
    except FileNotFoundError:
        return {}
    
def getImageThumbnail(_uuid: str):
    response = requests.get(
        f'{BACKEND_URL}/image/thumbnail',
        params={'_uuid': _uuid},
        stream=True,
        timeout=5
    )
    if response.status_code != 200:
        return Response("Thumbnail fetch failed", status=404)
    
    logging.info("Thumbnail fetched for %s", _uuid)
    return Response(
        response.content,
        status=200,
        content_type=response.headers.get("Content-Type", "image/jpeg")
    )
    
def getImage(_uuid: str):
    response = requests.get(
        f'{BACKEND_URL}/image',
        params={'_uuid': _uuid},
        stream=True,
        timeout=5
    )
    if response.status_code != 200:
        return Response("Thumbnail fetch failed", status=404)
    
    logging.info("Thumbnail fetched for %s", _uuid)
    return Response(
        response.content,
        status=200,
        content_type=response.headers.get("Content-Type", "image/jpeg")
    )