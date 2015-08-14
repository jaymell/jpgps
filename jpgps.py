"""
James's JPG GPS Module
"""

import exifread
from os import listdir
from os.path import isfile, join
import os
# for sys.argv:
import sys
import getopt
import datetime

gps_tags = [ 	'GPS GPSLongitude'	,
		'GPS GPSLatitude'	,
		'GPS GPSLatitudeRef'	,
		'GPS GPSAltitudeRef'	,
		'GPS GPSLongitudeRef'	,
		'GPS GPSAltitude' ]

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

class jpgps:
	def __init__(self, fi):
		self.image = fi
		self.latitude = self.return_coords()[0]	
		self.longitude = self.return_coords()[1]
		self.date = self.parse_date()

	def return_coords(self):
		g = open(self.image,'rb')
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

		return(lat_decimal,long_decimal)

	def parse_date(self):
	        g=open(self.image,'rb')
		tags = exifread.process_file(g)
		raw_date=tags['EXIF DateTimeOriginal']
		year,month,day=str(raw_date).split(' ')[0].split(':')[:]
		hour,minute,second=str(raw_date).split(' ')[1].split(':')[:]
		date=datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(second))
		return(date)

	def print_tag_names(self,):
		g=open(self.image,'rb')
		tags = exifread.process_file(g)
		for tag in tags.keys():
		    if tag in gps_tags:
			print "Key: %s, value %s" % (tag, tags[tag])
	
	def read_all_tags(self):
		g=open(self.image,'rb')
		tags = exifread.process_file(g)
		for tag in tags:
			if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
				print("Key: %s, value %s" % (tag, tags[tag]))

	

