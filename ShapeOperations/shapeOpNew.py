import rasterio.crs as rioCRS
import rasterio.transform as rioTransform
import fiona
from fiona.collection import Collection as FionaFile
from affine import Affine
import numpy as np
from ultralytics.engine.results import Boxes as uResultBoxes


# type GEOJSON = dict # type: ignore
def boxTensorTo_xywh(box: uResultBoxes) -> tuple[int, int, int, int]:
    x, y, w, h, = box.xywh[0]
    
    xtl = int(np.round(max(0, x-w/2)))
    ytl = int(np.round(max(0, y-h/2)))
    
    return ytl, xtl, int(h), int(w)
    

def makeBoxFeature(y: int, x: int, height: int, width: int, crs: rioCRS.CRS, transform: Affine, properties: dict={}, offset: str='ul') -> dict:
    """
    Generates a feature GEOJSON object that can be written to a shape file
    
    :param y: y Position of TL corner measured from UL (Upper Left in rasterio)
    :type y: int
    :param x: x Position of TL corner measured from UL (Upper Left in rasterio)
    :type x: int
    :param height: Height of the box in pixels
    :type height: int
    :param width: Width of the box in pixels
    :type width: int
    :param crs: CRS from raster
    :type crs: rioCRS.CRS
    :param transform: Transform from raster
    :type transform: Affine
    """
    
    assert offset in ['ul', 'll', 'ur', 'lr']
    
    x_tl, y_tl = rioTransform.xy(transform, rows=y, cols=x, offset=offset)
    x_br, y_br = rioTransform.xy(transform, rows=y+height, cols=x+width, offset=offset)
    
    # Polycon looped
    coords = [
        (x_tl, y_tl),
        (x_br, y_tl),
        (x_br, y_br),
        (x_tl, y_br),
        (x_tl, y_tl)    # Last point should be same as first as per RFC 7946
    ]
    
    feature = {
        'geometry': {
            'type': 'Polygon',
            'coordinates': [coords]
        },
    }
    
    if properties:
        feature['properties']=properties
    
    return feature

def makeShapeFile(*features:dict, crs: rioCRS.CRS, outFile: str, schema_properties: dict={}):
    """
    Builds a shape file from the features
    
    :param features: Description
    :type features: GEOJSON
    :param crs: Description
    :type crs: rioCRS.CRS
    :param outFile: Description
    :type outFile: str
    :param schema_properties: Description
    :type schema_properties: dict
    """
    schema = {
        'geometry': 'Polygon',
    }
    
    if schema_properties:
        schema['properties'] = schema_properties
    
    profile = {
        'driver': 'ESRI Shapefile',
        'crs': crs,
        'schema': schema
    }
    
    with fiona.open(outFile, 'w', **profile) as out:
        for feature in features:
            out.write(feature)