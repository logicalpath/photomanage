exiftool -d '%Y%m%d-%H%M%%-03.c.%%e' '-filename<CreateDate' Christmas\ 2007_20071224_266.JPG

# exiftool '-filename<%f-${location}.%e' DIR

# exiftool -filename -gpslatitude -gpslongitude -n -T . > out.txt