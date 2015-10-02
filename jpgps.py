import exifread
from os import listdir
from os.path import isfile, join
import os
# for sys.argv:
import sys
import getopt
import datetime
import re

""" convert date and gps data from exif meta in jpegs to something
	useable -- good reference for the fields:
	http://www.opanda.com/en/pe/help/gps.html """

class Jpgps:
	""" takes a jpg filname and creates Jpgps object for easy access of GPS 
		data on file; file doesn't have to actually be GPS-tagged, as 
		it still may be useful to access some of the metadata, eg date,
		even in absence of GPS data  -- use Jpgps.is_gps_tagged for checking """

	gps_tags = [ 	'GPS GPSLongitude'	,
			'GPS GPSLatitude'	,
			'GPS GPSLatitudeRef'	,
			'GPS GPSAltitudeRef'	,
			'GPS GPSLongitudeRef'	,
			'GPS GPSAltitude' 	,
		   ]

	def __init__(self, fi):
		self.image = fi
		try:
			with open(self.image, 'rb') as f:
				self.tags = exifread.process_file(f)		
		except Exception as e:
			print('Failed to open file: %s: %s' % (self.image,e))
			
	def __str__(self):
		return self.image

	def is_gps_tagged(self):
		match=0
		if all(k in self.tags for k in self.gps_tags):
			return True
		else: 	
			return False

	def print_gps_tags(self):
		for tag in self.tags.keys():
		    if tag in self.gps_tags:
			print "Key: %s, value %s" % (tag, self.tags[tag])
	
	def print_all_tags(self):
		""" well, all tags but 'JPEGThumbnail', 
			'TIFFThumbnail', 'Filename', 'EXIF MakerNote' """
		for tag in self.tags:
			if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
				print("Key: %s, value %s" % (tag, self.tags[tag]))

	def coordinates(self):
		""" strip out latitude, longitude info and return... data is stored
			in degree/minute/second/cardinal direction format, convert to
			+/- decimal degrees --- data type of dict values requires first
			converting to string, then numeric"""

		def convert_to_decimal(data, cardinal):
			""" takes the latitude/longitude data and associated cardinal
				direction and returns decimal W and S values considered
				negative """
			# degrees and minutes are integers:
			degrees, minutes = [ float(str(i)) for i in data.values[:2] ]
			# seconds may or may not be a ratio:
			seconds = self._standardize_num(data.values[2])
			flip = (-1) if (cardinal.values == 'W' or cardinal.values == 'S') else 1
			return flip * (degrees + minutes/60 + seconds/3600)

		if self.is_gps_tagged():
			latitude = convert_to_decimal(self.tags['GPS GPSLatitude'],self.tags['GPS GPSLatitudeRef'])
			longitude = convert_to_decimal(self.tags['GPS GPSLongitude'],self.tags['GPS GPSLongitudeRef'])
			return (latitude, longitude)
		else:
			return (None, None)
	def altitude(self, unit='feet'):
		""" read altitude, convert to feet --- some photos report
			'GPS GPSAltitude' as a fraction, others as integer, 
			so be able to handle appropriately """

		# set this to whatever you multiply meters by to get feet:
		############ FIX THIS ####################
		conversion = 69
		############ FIX ABOVE ###################
		if self.is_gps_tagged():
			altitude_meters = self.tags['GPS GPSAltitude'].values
			if self.tags['GPS GPSAltitudeRef']  == 0: 
				flip = 1
			elif self.tags['GPS GPSAltitudeRef'] == 1:	
				flip = -1
			else: 
				raise ValueError('Unexpected value for GPS GPSAltitudeRef')

			if unit == 'feet':
				return flip * ( altitude_meters * conversion)
			elif unit == 'meters':
				return flip * altitude_meters
			else:
				raise ValueError('Unexpected value for unit')
		else:
			return None
		
	def date(self):
		""" parse date string, return datetime object --
			may make more sense to use datetime.strftime
			for this """
		raw_date = self.tags['EXIF DateTimeOriginal']
		year, month, day = str(raw_date).split(' ')[0].split(':')[:]
		hour, minute, second = str(raw_date).split(' ')[1].split(':')[:]
		date = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(second))
		return (date)

	def _standardize_num(self, value):
		""" expects a either an integer or fraction, otherwise
			raise TypeError; if fraction, divides it and returns floating point;
			if integer, just return it as int -- done for minutes and altitude, which
			are prone to appear in either form """

		value = str(value)
		match = re.match('(\d*)/(\d*)', value)
		if match:
			numer = float(match.group(1))
			denom = float(match.group(2))
			return numer/denom
		else: 
			match = re.match('\d*', value)
			if match: 
				return int(value)
			else:
				raise TypeError('Unexpected format')



