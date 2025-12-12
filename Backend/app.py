from flask import Flask
from dotenv import load_dotenv
import os

backendApp = Flask("Backend App")

# ------------------ Load ENV Variables ------------------ #

print("Load ENV:", load_dotenv())

_baseUrl=os.getenv('base_url')
PORT=int(os.getenv("backend_port"))    # type: ignore
INFERENCE_URL = f'{_baseUrl}{os.getenv("inference_port")}'
SHAPEOP_URL = f'{_baseUrl}{os.getenv("shapeOp_port")}'
IMAGEOP_URL = f'{_baseUrl}{os.getenv("imageOp_port")}'
del _baseUrl

DEBUG = bool(os.getenv("DEBUG"))

# -------------------------------------------------------- #


backendApp.run(port=PORT, debug=DEBUG)