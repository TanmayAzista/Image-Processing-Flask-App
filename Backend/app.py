from dotenv import load_dotenv
print("Load ENV:", load_dotenv())

from flask import Flask, jsonify, request, send_file
import traceback
import os
import Backend.helpers as backendHelpers
import common_helpers
from io import BytesIO

backendApp = Flask("Backend App")

# ------------------ Load ENV Variables ------------------ #


_baseUrl=os.getenv('base_url')
PORT=int(os.getenv("backend_port"))    # type: ignore
INFERENCE_URL = f'{_baseUrl}:{os.getenv("inference_port")}'
SHAPEOP_URL = f'{_baseUrl}:{os.getenv("shapeOp_port")}'
IMAGEOP_URL = f'{_baseUrl}:{os.getenv("imageOp_port")}'
del _baseUrl

DEBUG = bool(os.getenv("DEBUG", 0))

# -------------------------------------------------------- #

# backendApp.route("/parse", methods=["POST"])
# def parseFile(fileName: str):

@backendApp.errorhandler(Exception)
def handle_exception(e):
    # Log error
    print("🔥 Unhandled Exception:")
    traceback.print_exc()

    # Return safe response
    return jsonify({
        "error": "Internal Server Error"
    }), 500

@backendApp.route("/file-saved", methods=["PUT"])
def fileSaved():
    _uuid, filename = common_helpers.get_requestArgs('_uuid', 'filename')

    backendHelpers.initialiseFile(_uuid, filename)

    return jsonify({
        "success": True,
        
    })

@backendApp.route("/image/thumbnail", methods=['GET'])
def getThumbnail():
    _uuid: str = common_helpers.get_requestArgs('_uuid')[0]
    thumbnail = backendHelpers.getThumbnail(_uuid)
    
    # print("Closed?", thumbnail.closed)
    # print("Buffer size:", thumbnail.getbuffer().nbytes)
    
    return send_file(
        BytesIO(thumbnail), 
        mimetype="image/jpeg",
        max_age=3600
    ) 

@backendApp.route("/image", methods=['GET'])
def getImage():
    _uuid: str = common_helpers.get_requestArgs('_uuid')[0]
    image = backendHelpers.getImage(_uuid)
    return send_file(
        BytesIO(image), 
        mimetype="image/png",
        max_age=3600
    )

backendApp.run(port=PORT, debug=DEBUG)