# ui-service/app.py
import os
import requests
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv


frontendApp = Flask("Frontend App")

# ------------------ Load ENV Variables ------------------ #

print("Load ENV:", load_dotenv())

_baseUrl=os.getenv('base_url')
PORT=int(os.getenv("frontend_port"))    # type: ignore
BACKEND_URL = f'{_baseUrl}{os.getenv("backend_port")}'
del _baseUrl

DEBUG = bool(os.getenv("DEBUG"))

# -------------------------------------------------------- #

# 



if __name__ == '__main__':
    frontendApp.run(port=PORT, debug=DEBUG)