from flask import Flask
from dotenv import load_dotenv
import os

inferenceApp = Flask("Inference App")

# ------------------ Load ENV Variables ------------------ #

print("Load ENV:", load_dotenv())

_baseUrl=os.getenv('base_url')
PORT=int(os.getenv("inference_port"))    # type: ignore
del _baseUrl

DEBUG = bool(os.getenv("DEBUG"))

# -------------------------------------------------------- #


@inferenceApp.get("/health")
def health():
    return {"status": "OK"}, 200


inferenceApp.run(debug=DEBUG, port=PORT)