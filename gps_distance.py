#!/usr/bin/python

import exifread
import sys
import math


#does photo have GPS tags?
#if yes, return True, else False:
def is_gps_tagged(fi):
	gps_tags=['GPS GPSLongitude','GPS GPSLatitude','GPS GPSLatitudeRef','GPS GPSAltitudeRef','GPS GPSDate','GPS GPSTimeStamp','GPS GPSLongitudeRef','GPS GPSAltitude']
        match=0
        g=open(fi,'rb')
        tags = exifread.process_file(g)
        for tag in tags.keys():
                if tag in gps_tags:
                        match=1
                        return True
        if match == 0:
                return False


def return_coords(fi):

        if not is_gps_tagged(fi):
                print("%s is not geo-tagged!" % fi)
                sys.exit(69)
        g = open(fi,'rb')
        tags = exifread.process_file(g)
        long_degrees = tags['GPS GPSLongitude'].values[0]
        long_minutes = tags['GPS GPSLongitude'].values[1]
        # separate numerator and divisor of the seconds for division:
        # for whatever reason, have to convert all to floats for division:
        long_seconds_num,long_seconds_div = str(tags['GPS GPSLongitude'].values[2]).split('/')
        long_seconds = float(float(long_seconds_num)/float(long_seconds_div))
        long_cardinal = tags['GPS GPSLongitudeRef'].values
        lat_degrees = tags['GPS GPSLatitude'].values[0]
        lat_minutes = tags['GPS GPSLatitude'].values[1]

        # do same math on latitude minutes as on longitude:
        lat_seconds_num,lat_seconds_div = str(tags['GPS GPSLatitude'].values[2]).split('/')
        lat_seconds = float(float(lat_seconds_num)/float(lat_seconds_div))
        lat_cardinal = tags['GPS GPSLatitudeRef'].values

        # degrees, minutes, seconds:    
        coords = [lat_degrees,lat_minutes,lat_seconds,lat_cardinal,long_degrees,long_minutes,long_seconds,long_cardinal]

        # convert to decimal:
        # have to first convert values to strings, then to integers/floats:
        lat_degrees = int(str(lat_degrees))
        lat_minutes = int(str(lat_minutes))
        lat_seconds = float(str(lat_seconds))
        long_degrees = int(str(long_degrees))
        long_minutes = int(str(long_minutes))
        long_seconds = float(str(long_seconds))

        # do final math to convert to decimal and append cardinal direction:
	# not passing cardinal directions: this will cause problems for cross-hemispheric 
	# comparisons but for now makes the math easier:
        lat_decimal = lat_degrees + lat_minutes/float(60) + lat_seconds/float(3600)
        long_decimal = long_degrees + long_minutes/float(60) + long_seconds/float(3600)

	# not working because these are LISTS, not ints or floats:
        return(lat_decimal,long_decimal)

def distance(pic1, pic2):
	
	p1_lat, p1_long = return_coords(pic1)[0:2]
	p2_lat, p2_long = return_coords(pic2)[0:2]
	
	radius = 6371 # radius of the Earths, in km
	#radius = 3963.1676 # miles
	dLat = math.radians(p1_lat-p2_lat)
	dLon = math.radians(p1_long-p2_long)
	lat1 = math.radians(p1_lat)
	lat2 = math.radians(p2_lat)

	a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2) 
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) 
	d = radius * c;
	
	# uhh, I think this is right -- results should be in unit of radius
	return(d)

pic1,pic2=sys.argv[1:3]
dist=distance(pic1,pic2)
print(dist)
