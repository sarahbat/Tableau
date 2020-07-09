# @sarahbat (Sarah Battersby)
#
# Read address data from csv, write geocoded results to csv
# Demo using kinda random Philadelphia addresses (from city Open data portal - real estate tax delinquincy data)
# Mapbox geocoder
# FWIW - Mapbox geocoder on ~10000 records ran for 46min 1s
# Mapbox's Temporary Geocoding API is free for up to 100,000 requests per month.

# Python = 2.7

import csv
import urllib
import json

file_input = r'philly_real_estate_tax_delinquencies_geocode_10k.csv'
file_output = r'philly_real_estate_tax_delinquencies_geocode_10k_output_mapbox.csv'
ID_FIELD = 0
ADDRESS_FIELD = 1
CITY_FIELD = 2
STATE_FIELD = 3
ZIP_FIELD = 4

MAPBOX_TOKEN = YOUR_API_KEY_HERE

with open(file_input) as csv_input:
	with open(file_output, 'w') as csv_output:
		csv_reader = csv.reader(csv_input, delimiter=',')
		csv_writer = csv.writer(csv_output, delimiter='|', lineterminator='\n')
		csv_writer.writerow(['address'] + ['city'] + ['state'] + ['zip'] + ['longitude'] + ['latitude'] + ['rowNum'] + ['id'] + ['accuracy'])

		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				line_count += 1
				continue
			else:
				if line_count % 100 == 0:
					# run off a counter to track progress
					print(line_count)
# 				print(line_count)
				# make address from relevant columns in csv (will vary depending on input format)
				address = row[ADDRESS_FIELD] + ',' + row[CITY_FIELD] + ',' + row[STATE_FIELD] + ' ' + row[ZIP_FIELD]
				id_val = row[ID_FIELD]
				# geocode using Mapbox; if match, write to csv
				# reformat location string for URL
				address = address.replace(' ', '+')
				geocode_url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/' + address + '.json?access_token=' + MAPBOX_TOKEN	
				try:
					req = urllib.request.Request(geocode_url)
					r = urllib.request.urlopen(req)
					req_body = r.read()

					j = json.loads(req_body)
					feature = j['features'][0]
				except:
					feature = {'properties': []}
					
	# 			print(feature)

				if 'accuracy' in feature['properties']:
					accuracy = feature['properties']['accuracy']
				else:
					accuracy = 'unknown'
				if 'center' in feature:
					lon = feature['center'][0]
					lat = feature['center'][1]
				else:
					lon = -99.0
					lat = -99.0

# 				print(feature)

				csv_writer.writerow([row[ADDRESS_FIELD]] + [row[CITY_FIELD]] +  [row[STATE_FIELD]] + [row[ZIP_FIELD]] + [lon] + [lat] + [line_count] + [row[ID_FIELD]] + [accuracy])

			line_count += 1
