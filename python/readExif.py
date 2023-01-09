from PIL import Image
from PIL.ExifTags import TAGS
import sys

def get_exif(filename):
    image = Image.open(filename)
    image.show()
    print(image._getexif())

    print('\nEXIF dictionary:\n')

    exif_table = {}
    for k, v in image._getexif().items():
        tags=TAGS.get(k)
        exif_table[TAGS[k]] = v

    print(exif_table)

def getAddress(lat, Long):
    # given signed decimal degress determine an address using ARCGis API
    # http://resources.esri.com/help/9.3/arcgisserver/apis/rest/geocode.html
    print("hello")


    



def main(args=None):
    if args is None:
        args = sys.argv[1:]
    
    #filename = args[0]
    filename = "/Users/eddiedickey/workspace/photomanage/photos/20071224-0951-000.JPG"
    
    get_exif(filename)



if __name__ == "__main__":
    main()