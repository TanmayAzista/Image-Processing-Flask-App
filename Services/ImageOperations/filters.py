import numpy as np
import cv2 as cv


def getAvgFilter(ksize: int) -> np.ndarray:
    """Returns avg filter for n x n filter"""
    return np.ones((ksize, ksize), np.float32) / (ksize ** 2)

def getGuassianFilter(ksize: int, sigma: float, ktype: int=cv.CV_32F) -> np.ndarray:
    assert ksize & 1, "Guassian K size should be odd and positive"
    
    return cv.getGaussianKernel(ksize, sigma, ktype)

def applyFilter(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    return cv.filter2D(img, -1, kernel)