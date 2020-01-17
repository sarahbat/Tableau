# -*- coding: utf-8 -*-
"""
Created on 1/17/2020

Demo of converstion between lat/lon and Google Plus Codes as part of a Tableau Prep workflow

Assumes that your location data is coming in from separate fields of latitude and longitude
or a single field with Google Plus code

If you need to convert addresses to latitude and longitude values first, I recommend checking out the 
Google Maps API for geocoding:
	developers.google.com/maps/documentation/geocoding

The Google Plus API does not require a Google API key.  Using a valid API key will return additional information
about the locality.  I have not provided examples here using the Google API key.  

The Google Plus API requires inclusion of an email address in the request regardless of whether or not you use 
an API key in your call to the service.

I have done *NO* research on costs associated with use of the Plus Codes API or what the implication is of
using your email address in the URL request.  Your mileage may vary.

@author: sarahbat
"""

import urllib
import json

def LatLng_to_GooglePlus(df):
	EMAIL_ADDRESS = 'YOUR_EMAIL_HERE'

	for i in range(0, len(df)):
		lat = df.iloc[i]['lat']
		lng = df.iloc[i]['lng']
		lat_lng = str(lat) + ',' + str(lng)

		plus_url = 'https://plus.codes/api?address=' + lat_lng + '&email=' + EMAIL_ADDRESS

		req = urllib.request.Request(plus_url)
		r = urllib.request.urlopen(req)
		req_body = r.read()
	    
		j = json.loads(req_body)
		if j['status'] == 'OK': # returned a valid json string; grab the Plus code
			df.set_value(i, 'plus_code', j['plus_code']['global_code'])
		else: # didn't return valid json string - sad :(
			df.set_value(i, 'plus_code', 'unknown')

	return df


def GooglePlus_to_LatLng(df):
	EMAIL_ADDRESS = 'YOUR_EMAIL_HERE'

	for i in range(0, len(df)):
		plus_code = df.iloc[i]['plus_code']

		# replace + with %2B for proper formatting for the URL call
		plus_code_format = plus_code.replace('+', '%2B')

		plus_url = 'https://plus.codes/api?address=' + plus_code_format + '&email=' + EMAIL_ADDRESS

		req = urllib.request.Request(plus_url)
		r = urllib.request.urlopen(req)
		req_body = r.read()
	    
		j = json.loads(req_body)
		if j['status'] == 'OK': # returned a valid json string; grab the lat/lng
			df.set_value(i, 'lat2', j['plus_code']['geometry']['location']['lat'])
			df.set_value(i, 'lng2', j['plus_code']['geometry']['location']['lng'])
		else: # didn't return valid json string - sad :(
			df.set_value(i, 'lat2', -999)
			df.set_value(i, 'lng2', -999)

	return df
