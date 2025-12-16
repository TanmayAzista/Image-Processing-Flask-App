from dotenv import load_dotenv
print("Load ENV:", load_dotenv())

from Helpers import common_helpers
from Services.ImageOperations import helpers as imageOpHelpers
from flask import Flask, send_file, Response, jsonify, request
import os
from io import BytesIO

imageOpApp = Flask("Image Operations App")

# ------------------ Load ENV Variables ------------------ #


_baseUrl=os.getenv('base_url')
PORT=int(os.getenv("imageOp_port"))    # type: ignore
del _baseUrl

DEBUG = bool(os.getenv("DEBUG", 0))

# -------------------------------------------------------- #

@imageOpApp.put("/transform")
def transformImage():
    npy_id, op = common_helpers.get_requestArgs("_uuid", "op")

    body = request.get_json(silent=True) or {}
    params = body.get("params", {})

    try:
        new_id = imageOpHelpers.applyTransform(npy_id, op, params)
    except NotImplementedError:
        return Response(
            "Invalid Transformation Operation"
        ), 400
    except FileNotFoundError:
        return Response(
            "Input image not found in stack"
        ), 404
        
    return jsonify({
        "transformation": f"transform.{op}",
        "input_uuid": npy_id,
        "output_uuid": new_id,
        "params": params
    }), 201



imageOpApp.run(port=PORT, debug=DEBUG)