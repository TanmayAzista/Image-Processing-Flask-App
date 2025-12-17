from Services.ImageOperations import helpers as imgOpHelpers
from Services.ImageOperations import colorCorrection as imgOpColorCorrection
from Services.Inference import model as inferenceModel

from Services.ShapeOperations import shapeOpNew as shapeOp
from ultralytics.engine.results import Results as uResults
from ultralytics import YOLO # type: ignore
import numpy as np
import os

MODEL_PATH = r"Inference\models\yolov8n.pt"
model = YOLO(MODEL_PATH)
model.to('cuda')

def getTifFiles(dir: str) -> list[str]:
    files = os.listdir(dir)
    files = list(filter(lambda x: os.path.splitext(x)[1] == '.tif', files))
    files = list(map(lambda x: os.path.splitext(x)[0], files))
    files = list(map(lambda file: os.path.join(dir, file), files))
    # Return files without any extension
    return files

def getNpFromTif(fileName: str) -> tuple[np.ndarray, dict]:
    image_raster = imgOpHelpers.loadRaster(fileName + '.tif')
    image = imgOpHelpers.rasterToNP(image_raster)
    image = imgOpColorCorrection.map_range(image, 0, 255)
    image = np.ascontiguousarray(image)
    
    raster_prop = {
        'crs': image_raster.crs,
        'transform': image_raster.transform
    }
    
    # Yolo Model prediction can only handle 3 channels.
    return image[:, :, :3], raster_prop

def modelPredict(images:list[np.ndarray]) -> list[uResults]:    
    # tif = list(map(getNpFromTif, files))
    inference = model.predict(images)
    return inference

def makeShapeFiles(inference: list[uResults], raster_prop: list[dict], files: list[str], schema_properties: dict = {}):
    names = inference[0].names
    for i, result in enumerate(inference):
        features = []
        r_prop = raster_prop[i]
        
        raster_crs = r_prop['crs']
        raster_transform = r_prop['transform']
        filename = files[i] + '.shp'
        
        for box in result.boxes:
            box = box.cpu().numpy()
            y, x, height, width = shapeOp.boxTensorTo_xywh(box)
            properties = {
            'id': int(box.cls[0]),
            'conf': box.conf[0],
            }
            
            properties['name'] = names[properties['id']]
            
            feature = shapeOp.makeBoxFeature(y, x, height, width, raster_crs, raster_transform, properties=properties)
            features.append(feature)
        shapeOp.makeShapeFile(*features, outFile=filename, crs=raster_crs, schema_properties=schema_properties)
    
    
def main():
    image_dir = r"D:\2092_TanmayVerma\ObjDetection_Flask\Data\Images\Clips"
    tif = getTifFiles(image_dir)
    print(f"Found {len(tif)} images")
    rasters = list(map(getNpFromTif, tif))
    images = list(map(lambda x: x[0], rasters))
    raster_prop = list(map(lambda x: x[1], rasters))
    
    print("Running Inference")
    inference = modelPredict(images)
    
    schema_prop = {
        'id': 'int',
        'name': 'str:20',
        'conf': 'float'
    }
    
    makeShapeFiles(inference, raster_prop, tif, schema_prop)
    
if __name__ == "__main__":
    main()