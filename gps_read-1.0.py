#!/usr/bin/python

import exifread
from os import listdir
from os.path import isfile, join
import os
# for sys.argv:
import sys
import getopt
import datetime

"""
GPS Keys:
Key: GPS GPSLongitude, value [97, 12, 10327/10000]
Key: GPS GPSLatitude, value [33, 2, 35377/1250]
Key: GPS GPSLatitudeRef, value N
Key: GPS GPSAltitudeRef, value 0
Key: GPS GPSDate, value 2013:11:03
Key: GPS GPSTimeStamp, value [16, 10, 43]
Key: GPS GPSLongitudeRef, value W
Key: GPS GPSAltitude, value 143
Format on google maps for coordinates: 
-- given: Key: GPS GPSLongitude, value [97, 12, 10327/10000]
Key: GPS GPSLatitude, value [33, 2, 35377/1250]
--
google maps: 33 2.3577N,97 12.10327 W
"""
############or: 33 2(35377/1250)N, 97 12(10327/10000)W = 33.02.28N 97.12.01W


#files=[f for f in listdir(path) if isfile(join(path,f))]
#gps_tags=['GPS GPSLongitude','GPS GPSLatitude','GPS GPSLatitudeRef','GPS GPSAltitudeRef','GPS GPSDate','GPS GPSTimeStamp','GPS GPSLongitudeRef','GPS GPSAltitude']
gps_tags=['GPS GPSLongitude','GPS GPSLatitude','GPS GPSLatitudeRef','GPS GPSAltitudeRef','GPS GPSLongitudeRef','GPS GPSAltitude']

def usage():
	print("\n\nUsage: %s <-p|-a|-i|-c|-d> <file name>\n" % sys.argv[0]) 
	print("\t-p:\tprint tag names")
	print("\t-a:\tprint ALL photo tags (with a couple exceptions")
	print("\t-i:\tis photo geo-tagged? If so, print file name and \"Yes\"")
	print("\t-c:\tprint COORDINATES of photo")
	print("\t-d:\tprint DATE of photo\n\n")
	quit()

def print_tag_names(fi):
	g=open(fi,'rb')
	tags = exifread.process_file(g)
	for tag in tags.keys():
	    if tag in gps_tags:
	     	print "Key: %s, value %s" % (tag, tags[tag])

#does photo have GPS tags?
#if yes, return True, else False:
def is_gps_tagged(fi):
	match=0
        g=open(fi,'rb')
        tags = exifread.process_file(g)
 	for tag in tags.keys():
	 	if tag in gps_tags:
			match=1
			return True
	if match == 0:
		return False

# print all tags, except for really long ones:		
def read_all_tags(fi):
	g=open(fi,'rb')	
	tags = exifread.process_file(g)
	for tag in tags:
		if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
			print("Key: %s, value %s" % (tag, tags[tag]))

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
	lat_decimal = [lat_degrees + lat_minutes/float(60) + lat_seconds/float(3600),lat_cardinal]
	long_decimal = [long_degrees + long_minutes/float(60) + long_seconds/float(3600),long_cardinal]
	
	print(lat_decimal,long_decimal)

def parse_date(fi):
	g=open(fi,'rb')
	tags = exifread.process_file(g)
	raw_date=tags['EXIF DateTimeOriginal']
	year,month,day=str(raw_date).split(' ')[0].split(':')[:]
	hour,minute,second=str(raw_date).split(' ')[1].split(':')[:]
	date=datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(second))
	print(date)

# where the main part starts:
try:
	opts,args = getopt.getopt(sys.argv[1:], "p:a:i:c:d:", ["print=", "all=", "is_tagged=","coord=","date="])
except getopt.GetoptError as err:
	print(str(err))
	usage()
	sys.exit(2)
for o, a in opts:
	if o in ["-p", "--print"]:
		fi=a
		print_tag_names(fi)
		sys.exit()	
	if o in ["-a", "--all"]:
		fi=a
		read_all_tags(fi)
		sys.exit()
	if o in ["-i", "--is_tagged"]:
		fi=a
		if is_gps_tagged(fi):
			print("%s Yes" % fi)
		sys.exit()
	if o in ["-c", "--cord"]:
		fi=a
		return_coords(fi)
		sys.exit()
	if o in ["-d", "--date"]:
		fi=a
		parse_date(fi)
		sys.exit()
	else:
		usage()
		sys.exit(2)

# if no options passed:
usage()
sys.exit(2)
