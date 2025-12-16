import rasterio.io as rioIO
import numpy as np
import os
from ImageOperations import helpers

def makeClips(img: np.ndarray, clip_size: int, overlap:float=0, save:bool=False, clip_name:str="", dir:str="", saveTypes:list[str]=["npy", "png", "tif"], src: rioIO.DatasetReader | None=None) -> list[np.ndarray]:
    """Generates square image clips from a larger image.
    
    :param img: The image with shape as (H, W) or (H, W, D)
    :type img: np.ndarray
    :param clip_size: The length of clip side in pixels
    :type clip_size: int
    :param overlap: How much should each clip overlap with any of its neighbouring clip.
    :type overlap: float 0~1
    :param save: Set to save the result
    :type save: bool
    :param clip_name: Prefix used while saving result
    :type clip_name: str
    :param dir: Directory to save the result
    :type dir: str
    :param saveTypes: Formats to save the result in
    :type saveTypes: list with values: ['npy', 'png', 'tif']
    :param src: Dataset Reader when opening raster via rasterio
    :type src: rioIO.DatasetReader | None
    """
    assert 2 <= len(img.shape) <= 3, "Invalid image shape"
    assert 0 <= overlap <= 1, "Define Overlap as float between 0~1"
    
    # Clip saving validation.
    can_save = save and clip_name != "" and saveTypes
    if save and not can_save:
        print("Please provide clip name prefix and saveTypes for saving. Skipping Save")

    # Fix shape to have all 3 values -> if grayscale, explicitly defines the layer as 1
    if len(img.shape) == 2:
        img = img[..., np.newaxis]
    (height, width, _) = img.shape       # (h, w, d)
    
    print("Starting")
    
    step_size = int(clip_size * (1 - overlap))      # Step Size to account for overlapping of clips. Clips overlap horizontally and vertically
    clips = []
    for y in range(0, height, step_size):
        for x in range(0, width, step_size):
            x_lim = x+clip_size
            y_lim = y+clip_size
            
            pad_x = max(0, x_lim-width)
            pad_y = max(0, y_lim-height)
            
            x_bound = min(x_lim, width)
            y_bound = min(y_lim, height)

            clip = img[y:y_bound, x:x_bound, :]
            
            if pad_x or pad_y:
                padding = (
                    (0, pad_y),
                    (0, pad_x),
                    (0, 0)
                )
                clip = np.pad(clip, padding, mode='constant', constant_values=0)
            
            # clip = img[y:y+clip_size, x:x+clip_size, :]
            clips.append(clip)

            if can_save:
                file_prefix = os.path.join(dir, f"{clip_name}_{y}_{x}")
                # NP file save
                if 'npy' in saveTypes:
                    helpers.saveNPY(clip, file_prefix)
                
                if 'png' in saveTypes:
                    helpers.savePNG(clip, file_prefix)
                
                if 'tif' in saveTypes:
                    assert src != None, "Source src required to save as .tif"
                    helpers.saveTif(clip, y, x, src.profile, src.transform, file_prefix)
                    
    print("Total Clips", len(clips))

    return clips
            
def main():
    
    image_file = r"D:\2092_TanmayVerma\ObjDetection_Flask\Data\Images\C2FMX020924PS014934.tif"
    
    raster = helpers.loadRaster(image_file)
    img_bands = helpers.rasterToNP(raster)
    
    makeClips(img_bands,clip_size=512, overlap=0.25, save=True, clip_name="karachi_clip_normalised", dir=r"D:\2092_TanmayVerma\ObjDetection_Flask\Data\Images\Clips", saveTypes=['tif'], src=raster)

if __name__ == "__main__":
    main()