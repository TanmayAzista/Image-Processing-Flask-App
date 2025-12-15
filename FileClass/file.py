import os
import pickle
import base64
import numpy as np
from enum import Enum
from io import BytesIO
from rasterio import io as rioIO
from PIL import Image as pilImage
from PIL import ImageFile as pilImageFile


# ------------------ Load ENV Variables ------------------ #
import dotenv
# dotenv.load_dotenv()      -> Should Ideally be loaded via app.py

_cwd = os.path.abspath(os.getcwd())
UPLOADS_DIR:str = os.getenv("uploads_dir", r"Data\Uploads")
UPLOADS_DIR = os.path.join(_cwd, UPLOADS_DIR)
os.makedirs(UPLOADS_DIR, exist_ok=True) # Makes directory if not present.
# -------------------------------------------------------- #

class FileExtensions(Enum):
    JPG = '.jpg'
    PNG = '.png'
    TIF = '.tif'
    TIFF = '.tiff'


class File:
    """File Object that stores intermediate results for processing accross services.  
    File.save_pkl() to use the pkl in other services.
    """
    def __init__(self, _uuid: str, filename: str):
        self._uuid = _uuid
        self.filename = filename
        _, self.ext = os.path.splitext(filename)
        pass
    
    @property
    def filename_pkl(self) -> str:
        return os.path.join(UPLOADS_DIR, f'{self._uuid}.pkl')
    
    @property
    def filepath(self) -> str:
        return os.path.join(UPLOADS_DIR, self._uuid+self.ext)
    
    def save_pkl(self):
        """Updates the pkl file with the new object"""
        try:
            with open(self.filename_pkl, 'wb') as file_pkl:
                pickle.dump(self, file_pkl)
            print(f"Updated {self.filename_pkl}")
        except Exception as e:
            print("Unable to save", self.filename_pkl)
            print(e)
    
    def __delete_files(self):
        """Deletes the associated files of the file"""
        from pathlib import Path
        for p in Path(UPLOADS_DIR).glob(self._uuid+"*"):
            p.unlink()
        
    def delete(self):
        mapp_file = os.path.join(UPLOADS_DIR, "mapping.pkl")
        with open(mapp_file, 'rb') as f:
            mapp = pickle.load(f)
        
        self.__delete_files()       # Remove all relevant files
        del mapp[self._uuid]        # Remove mapping
        
        with open(mapp_file, 'wb') as f:
            pickle.dump(mapp, f)    # Save new mapping
        
        del self                    # Delete object


class ImageFile(File):
    """Class for standard image file."""
    def __init__(self, _uuid, filename):
        super().__init__(_uuid, filename)
        self.read()
    
    @property
    def __npy_file_path(self):
        return os.path.join(UPLOADS_DIR, self._uuid + '.npy')
    
    @property
    def npy(self) -> np.ndarray:
        """Reads npy from .npy file if exists and returns np.ndarray"""

        if os.path.exists(self.__npy_file_path):
            return np.load(self.__npy_file_path)
        else:
            raise FileNotReadError
        
    @npy.setter
    def npy(self, val: np.ndarray):
        """Saves image as npy file in uploads dir"""
        with open(self.__npy_file_path, "wb") as f:
            np.save(f, val)
    
    @property
    def npy8(self):
        """Returns the npy in uint8"""
        _npy = self.npy
        if _npy.dtype == np.uint8:
            return _npy
        
        # def map_range(img: np.ndarray, outmin=0, outmax=255, outType=np.uint8) -> np.ndarray:
        _min, _max = np.min(_npy), np.max(_npy)
        _range = _max - _min
        normalised_img = (_npy - _min) / _range
        range_mapped = np.uint8(normalised_img * 255)
        print("8 bit conversion of image", range_mapped.shape, range_mapped.dtype)
        return range_mapped
    
    @property
    def image_render(self):
        return self.npy8[:, :, :3]
    
    @property
    def thumbnail(self):
        """Returns a base64 64x64 thumbnail image"""
        pil_img = pilImage.fromarray(self.image_render)
        pil_img = pil_img.resize((64, 64), pilImage.Resampling.LANCZOS)
        
        return ImageFile.to_bytes(np.array(pil_img))
    
    @property
    def image_full(self):
        return ImageFile.to_bytes(self.image_render, format="PNG")
        
    @staticmethod
    def to_bytes(img: np.ndarray, format="JPEG") -> bytes:
        pimg = pilImage.fromarray(img)

        buf = BytesIO()
        pimg.save(buf, format=format)
        # buf.seek(0)

        return buf.getvalue()
    
    @staticmethod
    def base64(img: np.ndarray) -> str:
        """Static method to convert from np.ndarry to base64 for rendering"""
        # ------------------------ Convert to Base 64 -------------------- #
        pimg = pilImage.fromarray(img)
        
        buffered = BytesIO()
        # Save the image to the buffer, specifying the format
        pimg.save(buffered, format="JPEG")
        # Get the byte value from the buffer
        img_bytes = buffered.getvalue()
        # Base64 encode the bytes
        base64_encoded_bytes = base64.b64encode(img_bytes)
        # Decode the bytes to a string for use in applications (e.g., HTML)
        base64_encoded_string = base64_encoded_bytes.decode('utf-8')
        
        return base64_encoded_string
    
    def __readJPG(self):
        """Read the original JPG and update details"""
        img = FileLoader.jpgLoader(self.filepath)
        self.npy = np.array(img)
    
    def __readPNG(self):
        """Read the original JPG and update details"""
        img = FileLoader.jpgLoader(self.filepath)
        self.npy = np.array(img)
    
    def __readTif(self):
        """Converts a raster loaded from rasterio to an np.ndarray
    
        Shape transposed from (D, H, W) -> (H, W, D)
        """
        img = FileLoader.tifLoader(self.filepath)
        
        bands = [img.read(i+1) for i in range(img.count)]
        _img_bands = np.stack(bands)
        _img_bands = _img_bands.transpose((1, 2, 0))
        
        self.npy = _img_bands
        
    def read(self):
        """Reads file and creates / updates .npy file in UPLOADS_DIR"""
        
        if self.ext == FileExtensions.JPG.value:
            self.__readJPG()
        elif self.ext == FileExtensions.PNG.value:
            self.__readPNG()
        elif self.ext in [FileExtensions.TIF.value, FileExtensions.TIFF.value]:
            self.__readTif()
        else:
            raise NotImplementedError("Unable to read fileformat", self.ext)
    
    def saveNPY(self):
        """Save npy file"""
        pass

class FileLoader:
    """Static methods for fileloading different types of files"""    
    @staticmethod    
    def jpgLoader(img_path) -> pilImageFile.ImageFile:
        img = pilImage.open(img_path)
        return img
    
    @staticmethod    
    def pngLoader(img_path) -> pilImageFile.ImageFile:
        img = pilImage.open(img_path)
        return img
    
    @staticmethod    
    def tifLoader(img_path) -> rioIO.DatasetReader:
        import rasterio
        return rasterio.open(img_path)

    
class FileNotReadError(Exception):
    def __init__(self) -> None:
        self.message = "File Not read, read with File.read()"
        super().__init__(self.message)