import fiona
from fiona.collection import Collection as FionaFile
from pyproj import CRS
from enum import Enum

road_file = r"D:\2092_TanmayVerma\ObjDetection_Flask\Data\Test_SHP\road.shp"
lulc_file = r"D:\2092_TanmayVerma\ObjDetection_Flask\Data\Test_SHP\lulc.shp"
box_file = r"D:\2092_TanmayVerma\ObjDetection_Flask\Data\Test_SHP\box_qgis.shp"

    
"""
PROFILE:: 
{
    "driver": "ESRI Shapefile",     -> Important
    "schema": {
        "properties": {             -> Meta
            "Id": "int32:9",
            "Type": "str:50",
            "Road_Width": "str:50",
            "Rd_name": "str:50",
            "Shape_Leng": "float:19.11"
        },
        "geometry": "LineString"    -> Important
    },
    "crs": "CRS.from_epsg(32644)",  -> Important
    "crs_wkt": "mathematical deifnition" -> Auto generated from CRS. Can be explicitly defined. Ground Truth when conflict with crs
}
"""
        
        
def load_vector(file: str):        
    with fiona.open(file) as shape:
        features = list(shape)
        profile = shape.profile
        
    del profile['crs_wkt']
    return features, profile


class ShapeTypes(Enum):
    """
    Possible ShapeTypes:
        Point
        MultiPoint
        LineString
        MultiLineString
        Polygon
        MultiPolygon
        GeometryCollection
    """
    Point="Point"
    MultiPoint="MultiPoint"
    LineString="LineString"
    MultiLineString="MultiLineString"
    Polygon="Polygon"
    MultiPolygon="MultiPolygon"
    GeometryCollection="GeometryCollection"


def makeProfile(shapeType: ShapeTypes, crs_epsg: int=-1, properties_schema=None):
    assert crs_epsg != -1, "CRS missing"
        
    profile = {
        "driver": "ESRI Shapefile",
        "schema": {
            "geometry": shapeType.value
        },
        "crs": CRS.from_epsg(crs_epsg)
    }
    
    if properties_schema:
        profile['schema']['properties'] = properties_schema
        
    return profile


def writeShape(shapeType: ShapeTypes, geometry: list | tuple, outFile: str | FionaFile, crs_epsg: int=-1, properties_schema=None, properties_values=None, mode: str='a'):
    """
    Writes a single shape / geometry to a shape file
    """
    
    assert shapeType in ShapeTypes, "ShapeType invalid. See help"
    assert len(mode) == 1, "Invalid file mode"
    assert mode in 'rwa', "Invalid file mode"
    
    geojson = {
        "geometry": {
            "type": shapeType.value,
            "coordinates": geometry
        },
        "properties": properties_values
    }   
    
    if isinstance(outFile, FionaFile):
        outFile.write(geojson)
    else:
        profile = makeProfile(shapeType, crs_epsg=crs_epsg, properties_schema=properties_schema)
        
        with fiona.open(outFile, mode, **profile) as out:
            out.write(geojson)

def main():
    box = [
        (219917, 3350798),
        (219917, 3362716),
        (210610, 3362716),
        (210610, 3350798),
        (219917, 3350798),
    ]
    outfile = r"D:\2092_TanmayVerma\ObjDetection_Flask\Data\Test_SHP\NewFile.shp"
    profile = makeProfile(shapeType=ShapeTypes.Point, crs_epsg=4326)
    with fiona.open(outfile, 'w') as outfile:
        for point in box:
            writeShape(shapeType=ShapeTypes.Point, geometry=point, outFile=outfile)
            
if __name__ == "__main__":
    # while 1:
    main()