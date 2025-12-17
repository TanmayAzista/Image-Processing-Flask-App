from ultralytics import YOLO # pyright: ignore[reportPrivateImportUsage]
import os
import numpy as np

MODEL_PATH = r"models\yolov8n.pt"
IMAGE_DIR = r"D:\2092_TanmayVerma\ObjDetection_Flask\Data\shipsnet\scenes\scenes"

def chooseImage(dir: str) -> str:
    """
    Allows user to select image. 
    Returns fully qualified path of the image.
    """
    # Images
    images = os.listdir(dir)
    # Choose image
    print("Available Images:")
    for i, img_file in enumerate(images):
        print(f"\t{i+1} :: {img_file}")
    
    try:
        while not (1 <= (img_chosen := int(input(f"Choose image (1 ~ {len(images)}): "))) <= len(images)):
            pass
    except ValueError:
        exit("Exiting")
    
    print("Image chosen: ", images[img_chosen-1])
    TEST_IMG = os.path.join(dir, images[img_chosen-1])
    return TEST_IMG


model = YOLO(MODEL_PATH)
model.to('cuda')


def inferenceImage(image):
    global model

    if isinstance(image, np.ndarray):
        assert image.dtype == np.uint8

    # Perform prediction on an image
    results = model.predict(image=image)

    # Process the results
    for i, result in enumerate(results):
        boxes = result.boxes
        print("Boxes")
        print(type(boxes))
        # print(boxes.data)
        # print(boxes.xyxy)
        print()
        
        # boxes = result.boxes  # Bounding box detections
        # masks = result.masks  # Instance segmentation masks (if applicable)
        # keypoints = result.keypoints # Pose/keypoints detections (if applicable)
        # probs = result.probs  # Probs object for classification outputs? Confidence?
        # names = result.names # Class names
        # print("OBB")
        # obb = result.obb
        # print(obb)
        # print()

        # You can then iterate through boxes, masks, etc., to extract information
        # for box in boxes:
        #     print(f"Detected object: {names[int(box.cls[0])]}, Confidence: {box.conf[0]:.2f}")
        
        # result.show()
        
        result.save(filename=f"shipInference{i}.jpg")
    
    return results


def main():
    # selected_img = chooseImage(IMAGE_DIR)
    from ..ImageOperations import helpers as imgOpHelpers
    
    image_path = r"D:\2092_TanmayVerma\ObjDetection_Flask\Data\Images\Clips\karachi_clip_normalised_2304_768.tif"
    image_raster = imgOpHelpers.loadRaster(image_path)
    image = imgOpHelpers.rasterToNP(image_raster)
    inference = inferenceImage(image)
    print(inference)
    

if __name__ == "__main__":
    while True:
        main()


# model.MODE(ARGS)