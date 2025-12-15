from dotenv import load_dotenv
print("Load ENV:", load_dotenv())

from flask import Flask
import os

shapeOpApp = Flask("Shape Operations App")

# ------------------ Load ENV Variables ------------------ #


_baseUrl=os.getenv('base_url')
PORT=int(os.getenv("shapeOp_port"))    # type: ignore
del _baseUrl

DEBUG = bool(os.getenv("DEBUG", 0))

# -------------------------------------------------------- #


shapeOpApp.run(port=PORT, debug=DEBUG)