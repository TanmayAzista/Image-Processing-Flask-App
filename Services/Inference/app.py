from dotenv import load_dotenv
print("Load ENV:", load_dotenv())

from flask import Flask
import os

inferenceApp = Flask("Inference App")

# ------------------ Load ENV Variables ------------------ #


_baseUrl=os.getenv('base_url')
PORT=int(os.getenv("inference_port"))    # type: ignore
del _baseUrl

DEBUG = bool(os.getenv("DEBUG", 0))

# -------------------------------------------------------- #


@inferenceApp.get("/health")
def health():
    return {"status": "OK"}, 200


inferenceApp.run(debug=DEBUG, port=PORT)