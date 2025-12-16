from ImageOperations import colorCorrection
import rasterio
import rasterio.profiles as rioProfiles
import rasterio.windows as rioWindows
import rasterio.io as rioIO
from affine import Affine
import numpy as np
from PIL import Image


def loadRaster(filePath: str) -> rioIO.DatasetReader:
    return rasterio.open(filePath)

def saveNPY(img: np.ndarray, outFile: str) -> None:
    try:
        with open(outFile + ".npy", "wb") as f:
            np.save(f, img)
    except Exception as e:
        print(f"Error saving {outFile}.npy", e)
    
def savePNG(img: np.ndarray, outFile: str) -> None:
    # PNG Save
    img = colorCorrection.clip_normalise_bandwise(img, clip_percent=2)
    img = colorCorrection.map_range(img)
    img_file = Image.fromarray(img[:, :, :3], 'RGB')
    try:
        img_file.save(outFile+".png")
    except Exception as e:
        print(f"Error saving {outFile}.png", e)
    
def saveTif(img: np.ndarray, y_start: int, x_start: int, src_profile:rioProfiles.Profile, src_transform: Affine, outFile:str) -> None:
    # NumPy shape is (H, W, D). Rasterio profile uses (W, H, Count)
    height, width, d_count = img.shape
    
    window = rioWindows.Window(
        col_off=x_start,    # type: ignore -> Works perfectly. Warning ignored.
        row_off=y_start,    # type: ignore
        width=width,        # type: ignore
        height=height       # type: ignore
    )
    
    newTransform = rioWindows.transform(
        window=window,
        transform=src_transform
    )
    
    profile = src_profile
    
    profile.update({
        'height': height,
        'width': width,
        'count': d_count,
        'transform': newTransform,
        'driver': 'GTiff', 
        'dtype': img.dtype
    })
    
    try:
        with rasterio.open(outFile + ".tif", 'w', **profile) as dst:
            dst.write(img.transpose(2, 0, 1))
    except Exception as e:
        print(f"Error saving {outFile}.tif", e)

def rasterToNP(img: rioIO.DatasetReader) -> np.ndarray:
    """Converts a raster loaded from rasterio to an np.ndarray
    
    Shape transposed from (D, H, W) -> (H, W, D)
    """
    bands = [img.read(i+1) for i in range(img.count)]
    img_bands = np.stack(bands)
    img_bands = img_bands.transpose((1, 2, 0))
    return img_bands