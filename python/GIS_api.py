from arcgis.gis import GIS
from arcgis.geocoding import geocode, reverse_geocode
from arcgis.geometry import Point
import appSettings as s

# exiftool -filename -gpslatitude -gpslongitude -n -T . > out.txt
# IMG_4102.JPG	37.7918055555556	-122.413277777778

api_key = s.apiKey
portal = GIS("https://www.arcgis.com", api_key=api_key)

location = {
     'Y': 37.7918055555556,                 # `Y` is latitude
     'X': -122.413277777778,               # `X` is longitude
     'spatialReference': {
         'wkid':4326
     }
}
unknown_pt = Point(location)
reverse_results = reverse_geocode(location=unknown_pt)
print (reverse_results)