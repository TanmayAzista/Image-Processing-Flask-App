from flask import Flask

from dotenv import load_dotenv
import os

shapeOpApp = Flask("Shape Operations App")

# ------------------ Load ENV Variables ------------------ #

print("Load ENV:", load_dotenv())

_baseUrl=os.getenv('base_url')
PORT=int(os.getenv("shapeOp_port"))    # type: ignore
del _baseUrl

DEBUG = bool(os.getenv("DEBUG"))

# -------------------------------------------------------- #


shapeOpApp.run(port=PORT, debug=DEBUG)