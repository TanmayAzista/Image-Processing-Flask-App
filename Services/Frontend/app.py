# ui-service/app.py
# load dotenv at the beginning always!
from dotenv import load_dotenv
print("Load ENV:", load_dotenv())


import os
from flask import Flask, render_template, jsonify, request
import Services.Frontend.helpers as frontHelpers
import Helpers.common_helpers as common_helpers
from werkzeug.exceptions import HTTPException
import logging


# ensure template/static paths are absolute so templates are found when running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

frontendApp = Flask("Frontend App", template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

# ------------------ Load ENV Variables ------------------ #


PORT=int(os.getenv("frontend_port"))    # type: ignore
DEBUG = bool(os.getenv("DEBUG", 0))

# -------------------------------------------------------- #


@frontendApp.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e  # let Flask handle it normally
    
    # Log error
    logging.exception("🔥 Unhandled Exception:")
    logging.exception("")
    # traceback.print_exc()

    # Return safe response
    return jsonify({
        "error": "Internal Server Error"
    }), 500


@frontendApp.route('/')
def index():
    return render_template('index.html')

# API endpoint to get image list
@frontendApp.route('/api/images', methods=['GET'])
def api_get_images():
    images = frontHelpers.getImageList()
    # Return as list of dicts: [{uuid:..., filename:...}, ...]
    return jsonify([
        {"uuid": uuid, "filename": filename}
        for uuid, filename in images.items()
    ])

# Proxy thumbnail route
@frontendApp.route('/image/thumbnail', methods=['GET'])
def getImageThumbnail():
    _uuid = common_helpers.get_requestArgs('_uuid')[0]
    return frontHelpers.getImageThumbnail(_uuid)


@frontendApp.route('/image', methods=['GET'])
def getImage():
    _uuid = common_helpers.get_requestArgs('_uuid')[0]
    return frontHelpers.getImage(_uuid)


@frontendApp.route('/upload', methods=['PUT'])
def fileUpload():
    """
    Copies the file to 'Data/Uploads'
    Renames file to uuid.ext and updates mapping.pkl
    """    
    file = request.files['file']
    filename = str(file.filename)
    _, ext = os.path.splitext(filename)
    file_uuid = common_helpers.generate_uuid()
    
    try:
        # Copy file as uuid to Uploads Dir
        # Outcome -> New file uuid.ext created in Uploads dir
        if not frontHelpers.saveFileToUploads(file_uuid, file):
            raise ChildProcessError
        
        # Inform backend that new file has been uploaded
        if not frontHelpers.backend_informFileUpload(file_uuid, str(file.filename)):
            raise Exception("Unsupported file type")
        
        # Add new mapping
        # Contains {uuid: filename} map
        if not frontHelpers.addFileMapping(file_uuid, filename):
            raise FileNotFoundError
    except Exception as e:
        frontHelpers.removeFile(file_uuid+ext)
        raise e
    
    return jsonify({
        "status": "success",
        "uuid": file_uuid,
        "original_filename": filename,
    }), 201



if __name__ == '__main__':
    frontendApp.run(port=PORT, debug=DEBUG)