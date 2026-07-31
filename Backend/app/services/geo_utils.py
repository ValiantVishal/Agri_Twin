from typing import List, Dict, Tuple
from shapely.geometry import Polygon
import pyproj
from shapely.ops import transform

# Define coordinates projection: EPSG:4326 (WGS84) to EPSG:32644 (UTM Zone 44N)
wgs84 = pyproj.CRS('EPSG:4326')
utm44n = pyproj.CRS('EPSG:32644')

# pyproj Transformer to convert coordinates
# always_xy=True ensures mapping is (lng, lat) -> (X, Y)
projector = pyproj.Transformer.from_crs(wgs84, utm44n, always_xy=True).transform


def is_polygon_valid(points: List[Dict[str, float]]) -> bool:
    """
    Check if the list of points forms a valid, non-self-intersecting polygon.
    """
    if len(points) < 3:
        return False
    
    coords = [(p['lng'], p['lat']) for p in points]
    if coords[0] != coords[-1]:
        coords.append(coords[0])
        
    poly = Polygon(coords)
    return poly.is_valid


def calculate_area_and_perimeter(points: List[Dict[str, float]]) -> Tuple[float, float, float, float]:
    """
    Calculate the area and perimeter of a polygon using UTM Zone 44N projection.
    
    Returns:
        (area_sqm, area_acres, area_cents, perimeter_m)
    """
    coords = [(p['lng'], p['lat']) for p in points]
    if coords[0] != coords[-1]:
        coords.append(coords[0])
        
    poly = Polygon(coords)
    projected_poly = transform(projector, poly)
    
    area_sqm = projected_poly.area
    perimeter_m = projected_poly.length
    
    # Land unit conversions:
    # 1 acre = 4046.8564 sqm
    # 1 cent = 40.4686 sqm (or 1/100th of an acre)
    area_acres = area_sqm / 4046.8564224
    area_cents = area_acres * 100.0
    
    return area_sqm, area_acres, area_cents, perimeter_m
