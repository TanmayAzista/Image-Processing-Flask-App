import numpy as np

def map_range(img: np.ndarray, outmin=0, outmax=255, outType=np.uint8) -> np.ndarray:
    _min, _max = np.min(img), np.max(img)
    normalised_img = (img - _min) / (_max - _min)
    range_mapped = outType(normalised_img * (outmax - outmin) + outmin)
    return range_mapped # type: ignore

def clip_normalise(img: np.ndarray, clip_percent: float = 2):
    assert 0 < clip_percent < 50, "Clip percent should be between 0 ~ 50"
    
    pixel_min, pixel_max = np.nanpercentile(img, (clip_percent, 100 - clip_percent))
    # return np.clip((img - pixel_min) / (pixel_max - pixel_min), 0, 1)
    return np.clip(img, pixel_min, pixel_max)

def clip_normalise_bandwise(img: np.ndarray, clip_percent: float = 2):
    assert 2 <= len(img.shape) <= 3, "Invalid image shape"
    if len(img.shape) == 2:
        img = img[..., np.newaxis]
        
    bands = [clip_normalise(img[:, :, i], clip_percent=clip_percent) for i in range(img.shape[2])]

    return np.stack(bands, axis=2)