#!/usr/bin/python

import exifread
from os import listdir
from os.path import isfile, join
import os
# for sys.argv:
import sys
import getopt
import datetime
import jpgps

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

def usage():
	print("\n\nUsage: %s <-p|-a|-i|-c|-d> <file name>\n" % sys.argv[0]) 
	print("\t-p:\tprint GPS tags")
	print("\t-a:\tprint ALL photo tags (with a couple exceptions)")
	print("\t-i:\tis photo geo-tagged? If so, print file name and \"Yes\"")
	print("\t-c:\tprint COORDINATES of photo")
	print("\t-d:\tprint DATE of photo\n\n")
	quit()

# where the main part starts:
try:
	opts,args = getopt.getopt(sys.argv[1:], "p:l:a:i:c:d:", ["print=", "altitude=", "all=", "is_tagged=","coord=","date="])
except getopt.GetoptError as err:
	print(str(err))
	usage()
	sys.exit(2)
else:
	for o, a in opts:
		if o in ["-p", "--print"]:
			fi=a
			fi = jpgps.Jpgps(fi)
			fi.print_gps_tags()
			sys.exit()	
		if o in ["-l", "--altitude"]:
			fi=a
			fi = jpgps.Jpgps(fi)
			print(fi.altitude())
			sys.exit()	

		if o in ["-a", "--all"]:
			fi=a
			fi = jpgps.Jpgps(fi)
			fi.print_all_tags()
			sys.exit()
		if o in ["-i", "--is_tagged"]:
			fi=a
			fi = jpgps.Jpgps(fi)
			if fi.is_gps_tagged():
				print("%s Yes" % fi)
			else: 
				print("%s No" % fi)
			sys.exit()
		if o in ["-c", "--cord"]:
			fi=a
			fi = jpgps.Jpgps(fi)
			print(fi.coordinates())
			sys.exit()
		if o in ["-d", "--date"]:
			fi=a
			fi = jpgps.Jpgps(fi)
			print(fi.date())
			sys.exit()
		else:
			usage()
			sys.exit(2)

# if no options passed:
usage()
sys.exit(2)
