from dotenv import load_dotenv
print("Load ENV:", load_dotenv())

from flask import Flask, jsonify, send_file, Response, request
import requests
import traceback
import os
import Services.Backend.helpers as backendHelpers
import Helpers.common_helpers as common_helpers
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


# ----------------------- Stack Init --------------------- #
# Load Stack manager on load

from Helpers.StackManager.stackManager import StackManager
stackManager = StackManager() 
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

@backendApp.route("/image", methods=['PUT'])
def setImage():
    _uuid: str = common_helpers.get_requestArgs('_uuid')[0]
    
    # Read Image and save copy to StackDir
    new_uuid = backendHelpers.imageSaveToStack(_uuid)

    # Add Image to stack
    stackManager.resetImage(new_uuid)
    
    return getImage()

@backendApp.route("/image", methods=['GET'])
def getImage():
    image: bytes | None = stackManager.getCurrentImage()
    if image is None:
        return Response("No Image"), 404
    
    return send_file(
        BytesIO(image), 
        mimetype="image/png",
        max_age=3600
    )

@backendApp.route("/stack", methods=["DELETE"])
def resetStack():
    try:
        stackManager.reset()
    except:
        return jsonify({
            "success": False
        }), 500        
        
    return jsonify({
        "success": True
    }), 200

@backendApp.route("/stack/state", methods=["GET"])
def getStackState():
    stack_size = len(stackManager.npy_stack)
    pointer = stackManager.current_pointer

    has_image = stack_size > 0
    is_dirty = stack_size > 1

    return jsonify({
        "has_image": has_image,
        "stack_size": stack_size,
        "current_pointer": pointer,
        "is_dirty": is_dirty,
        "undo_possible": stackManager.undoPossible,
        "redo_possible": stackManager.redoPossible
    }), 200

@backendApp.route("/stack/undo", methods=["POST"])
def undoStack():
    return jsonify({
        "success": stackManager.undo(),
        "stack_pointer": stackManager.current_pointer,
        "undo_possible": stackManager.undoPossible,
        "redo_possible": stackManager.redoPossible
    }), 200
    
@backendApp.route("/stack/redo", methods=["POST"])
def redoStack():
    return jsonify({
        "success": stackManager.redo(),
        "stack_pointer": stackManager.current_pointer,
        "undo_possible": stackManager.undoPossible,
        "redo_possible": stackManager.redoPossible
    }), 200

@backendApp.route("/transform", methods=["PUT"])
def applyTransform():
    if stackManager.current_pointer < 0:
        return Response("No active image selected"), 400

    body = request.get_json(silent=True) or {}
    op = body.get("op")
    
    if not op:
        return Response("Missing transform operation"), 400

    params = body.get("params", {})

    input_id = stackManager.npy_stack[stackManager.current_pointer]

    try:
        resp = requests.put(
            f"{IMAGEOP_URL}/transform",
            params={
                "_uuid": input_id,
                "op": op
            },
            json={"params": params},
            timeout=60
        )
    except requests.RequestException as e:
        return Response(f"ImageOp service unavailable: {e}"), 502

    if resp.status_code != 201:
        return Response(resp.text, resp.status_code)

    data = resp.json()
    new_id = data.get("output_uuid")
    if not new_id:
        return Response("Invalid response from ImageOp"), 500

    stackManager.addImage(new_id)

    return jsonify({
        "status": "success",
        "operation": op,
        "input_uuid": input_id,
        "output_uuid": new_id,
        "stack_pointer": stackManager.current_pointer,
        "undo_possible": stackManager.undoPossible,
        "redo_possible": stackManager.redoPossible
    }), 201


backendApp.run(port=PORT, debug=DEBUG)