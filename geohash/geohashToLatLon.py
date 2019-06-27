# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 12:07:19 2019

Super quick bit of code to convert from geohash to lat/lon

@author: sbattersby
"""

import pygeohash as pgh
import csv


# open csv with geohash data
r_file = open('d:\\Python\Tableau\geohash to lat lon\latlongInput.csv', mode = 'r')
r_reader = csv.reader(r_file)

# open output csv to hold geohash and lat/lon output
geo_file = open('d:\\Python\Tableau\geohash to lat lon\geohashOutput.csv', mode = 'w', newline = '')
geo_writer = csv.writer(geo_file, delimiter = ',', quotechar = '"')
geo_writer.writerow(['geohash', 'long', 'lat'])

# translate the geohash to lat/lon and write to new file
row_count = 0
for row in r_reader:
    if row_count == 0: # header
        pass
    else:
        gh = row[2]
        latlon = pgh.decode(row[2])
        geo_writer.writerow([gh, latlon[1], latlon[0]])
    row_count += 1

r_file.close()
geo_file.close()
    
