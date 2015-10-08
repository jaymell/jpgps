#!/usr/bin/python

import argparse
import jpgps
import logging
# for dumping errors to stderr:
logging.basicConfig()

parser = argparse.ArgumentParser(description='CLI utility for extracting exif GPS information')

parser.add_argument("-a", "--altitude", action="store_true", default=False, help="include altitude (in feet)")
parser.add_argument("-i", "--is-tagged", action="store_true", default=False, help="only report whether photo is geo-tagged")
parser.add_argument("-d", "--date", action="store_true", default=False, help="include photo date")
parser.add_argument("-v", "--verbose", action="count", default=0)
parser.add_argument("file_list", nargs="+")

args = parser.parse_args()

if not args.is_tagged:
	header = "File Latitude Longitude "
	if args.altitude:
		header += "Altitude "
	if args.date:
		header += "Date "
	print(header)
	for i in args.file_list:
		try:
			fi = jpgps.Jpgps(i)
		except Exception as e:
			print('Failed to open %s: %s' % (i, e))
		else:
			latitude, longitude = fi.coordinates()
			result = "%s %s %s " % (fi.image, latitude, longitude)
			if args.altitude: 
				result += "%s " % fi.altitude()
			if args.date:
				result += "%s " % fi.date()
			print(result)	
			if args.verbose:
				fi.get_tags(verbose=args.verbose, stdout=True)
else:
	for i in args.file_list:
                try:
                        fi = jpgps.Jpgps(i)
                except Exception as e:
                        print('Failed to open %s: %s' % (i, e))
                else:
			if fi.is_gps_tagged():
				print("%s Yes" % fi.image)
			else:
				print("%s No" % fi.image)
	 
