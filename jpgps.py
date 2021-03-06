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

	def __init__(self, fi):
		self.image = fi.name
		self.tags = exifread.process_file(fi)		

	def __str__(self):
		return self.image

	def is_gps_tagged(self):
		""" determines whether to consider image to be
			gps-tagged or not -- there are other
			GPS tags, however """

		gps_tags = [ 	'GPS GPSLongitude'	,
				'GPS GPSLatitude'	,
				'GPS GPSLatitudeRef'	,
				'GPS GPSAltitudeRef'	,
				'GPS GPSLongitudeRef'	,
				'GPS GPSAltitude' 	,
			   ]


		match=0
		if all(k in self.tags for k in gps_tags):
			return True
		else: 	
			return False

	def get_tags(self, verbose=0, stdout=False):
		""" returns tags, by default GPS only, with
			additional based on verbosity level """ 

		thumbnail_tags = ['TIFFThumbnail', 'JPEGThumbnail']
		if verbose >= 3:
			selected = self.tags
		elif verbose >= 2:
			selected = { x: y for x,y in self.tags.items() if x not in thumbnail_tags }
		elif verbose >= 1:
			selected = { x: y for x,y in self.tags.items() if x.startswith('GPS') }

		if stdout == True:
			for key, value in selected.items(): print('%s: %s' % (key, value))
		return selected

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
		conversion = 3.28084
		if self.is_gps_tagged():
			altitude_meters = int(self.tags['GPS GPSAltitude'].printable)
			altitude_ref = int(self.tags['GPS GPSAltitudeRef'].printable)
			if altitude_ref == 0: 
				flip = 1
			elif altitude_ref == 1:	
				flip = -1
			else: 
				# overly cautious type checking:
				raise ValueError('Unexpected value for GPS GPSAltitudeRef')

			if unit == 'feet':
				return round(flip * ( altitude_meters * conversion),0)
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
		if 'EXIF DateTimeOriginal' in self.tags:
			raw_date = self.tags['EXIF DateTimeOriginal']
			year, month, day = str(raw_date).split(' ')[0].split(':')[:]
			hour, minute, second = str(raw_date).split(' ')[1].split(':')[:]
			return datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),int(second))
		else:
			return None

	def dimensions(self):
		""" return width, height in pixels """

		
		if 'EXIF ExifImageWidth' and 'EXIF ExifImageLength' in self.tags:
			try:
				# tuple:
				return (int(self.tags['EXIF ExifImageWidth'].printable), 
					int(self.tags['EXIF ExifImageLength'].printable))
			except Exception as e:
				raise ValueError('Unexpected value for dimensions: %s' % e)
		return None

	def orientation(self):
		""" return exif orientation data (photo rotation) """

		if 'Image Orientation' in self.tags:
			orientation_raw = self.tags['Image Orientation'].values
			# very specific type checking to make sure no unexpected 
			# formats appears in data:
			if type(orientation_raw) != list and len(orientation_raw) != 1:
				raise ValueError('Unexpected value for Image Orientation')
				return None
			else:
				return int(str(orientation_raw[0]))

	def rotation(self):
		""" return number of degrees image is rotated """

		oriented = self.orientation()
		if oriented:
			if (oriented == 3 or oriented == 4):
				return 180
			elif (oriented == 5 or oriented == 6):
				return 270
			elif (oriented == 7 or oriented == 8):
				return 90
			else:
				return 0
		else:
			return None
			
	def as_dict(self):
		return {'file_name': self.image,
			'latitude': self.coordinates()[0] if self.coordinates() else None,
			'longitude': self.coordinates()[1] if self.coordinates() else None,
			'date': self.date().strftime('%Y-%m-%d %H:%M:%S') if self.date() else None,
			'width': self.dimensions()[0] if self.dimensions() else None,
			'height': self.dimensions()[1] if self.dimensions() else None,
			}
			

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
