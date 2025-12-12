from flask import Flask

from dotenv import load_dotenv
import os

imageOpApp = Flask("Image Operations App")

# ------------------ Load ENV Variables ------------------ #

print("Load ENV:", load_dotenv())

_baseUrl=os.getenv('base_url')
PORT=int(os.getenv("imageOp_port"))    # type: ignore
del _baseUrl

DEBUG = bool(os.getenv("DEBUG"))

# -------------------------------------------------------- #


@imageOpApp.get("/images")
def getImages():
    imagedir = os.getenv("image_dir")
    return {"images": os.listdir(imagedir)}, 200

@imageOpApp.get("/health")
def getHealth():
    return {"status": "OK"}, 200

imageOpApp.run(port=PORT, debug=DEBUG)