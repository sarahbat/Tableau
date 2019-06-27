#### 
# For when I need to quickly make some fake data
####

import csv

numValues = 100
geohashPrecision = 6

# make a csv with random lat/lon and geohash coordinates
w_file = open('d:\\Python\Tableau\geohash to lat lon\latlongInput.csv', mode = 'w', newline = '')
w_writer = csv.writer(w_file, delimiter = ',', quotechar = '"')
w_writer.writerow(['long', 'lat', 'geohash'])
for i in range(0, numValues):
    long = random.randrange(-1800, 1800) / 10
    lat = random.randrange(-900, 900) / 10
    geohash = pgh.encode(lat, long, geohashPrecision)
    w_writer.writerow([ long, lat, geohash ])
w_file.close()
