from FileClass.file import ImageFile
from functools import lru_cache
from io import BytesIO
import pickle
import os

# ------------------ Load ENV Variables ------------------ #
import dotenv
# dotenv.load_dotenv()      -> Should Ideally be loaded via app.py

_baseUrl=os.getenv('base_url')
INFERENCE_URL = f'{_baseUrl}:{os.getenv("inference_port")}'
SHAPEOP_URL = f'{_baseUrl}:{os.getenv("shapeOp_port")}'
IMAGEOP_URL = f'{_baseUrl}:{os.getenv("imageOp_port")}'
del _baseUrl

_cwd = os.path.abspath(os.getcwd())
UPLOADS_DIR:str = os.getenv("uploads_dir", r"Data\Uploads")
UPLOADS_DIR = os.path.join(_cwd, UPLOADS_DIR)
os.makedirs(UPLOADS_DIR, exist_ok=True) # Makes directory if not present.

# -------------------------------------------------------- #

def initialiseFile(_uuid: str, filename: str):
    """Initialises a File type object and saves a pkl file"""
    newFile = ImageFile(_uuid, filename)
    newFile.save_pkl()


@lru_cache
def getThumbnail(_uuid: str) -> bytes:
    img: ImageFile = getPickle(_uuid)
    return img.thumbnail


@lru_cache
def getPickle(_uuid: str) -> ImageFile:
    """Returns the File Object (Probably ImageFile) Handle FileNotExist manually in when calling this function"""
    pkl_file = os.path.join(UPLOADS_DIR, _uuid + ".pkl")
    with open(pkl_file, 'rb') as pkl:
        return pickle.load(pkl)
        
@lru_cache
def getImage(_uuid: str) -> bytes:
    img: ImageFile = getPickle(_uuid)
    return img.image_full