## Synopsis
Module and CLI util to quickly get date, GPS coordinates, and altitude out of geotagged JPEG files (not tested
with other formats, though may work for TIFFs)

## Motivation
Getting data out of images that is useful for plotting thumbnails on map and
otherwise determining relative positions between photos.

## Dependencies
* python modules: exifread
  * pip install -r requirements.txt

## Future improvements:
1. Need to test for ratios in ALL values of longitude and latitude fields -- even
though I haven't encountered this, definite possiblity given that this is how exif
spec claims it's reported
2. Better handling of date -- there are lots of tags to get it from, but if photo is actually
GPS-tagged, probably more accurate to use GPS time/date stamps and do time-zone correction.
The possiblities -- could probably prioritize them and choose accordingly:
  * Image DateTime
  * EXIF DateTimeOriginal
  * EXIF DateTimeDigitized
  * GPS GPSDate 
  * GPS GPSTimeStamp

## Misc.
* gps_distance.py is old code and probably buggy, but keeping it in repo for now, may update
it later

