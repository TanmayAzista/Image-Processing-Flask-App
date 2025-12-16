import uuid
import base64
import os
import pickle
import dotenv
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