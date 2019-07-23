# -*- coding: utf-8 -*-
"""
Created on 7/23/19

Demo of geocoding to convert address strings to lat/lon as part of a Tableau Prep workflow

Assumes that your address is coming in from separate fields of Address, City, State, Zip...modify the query to fit 
whatever you are using for input.  All you need to do it mush everythign together into a single string to pass
to the geocoding service.

Also assumes that you have a file with fields for Latitude, Longitude, and accuracy for the geocoding output 
(I added those with a step in my Tableau Prep workflow, then ran the script)

Please pay attention to needs for API key, as well as licensing restrictions on whatever service you use

When using this with Tableau Prep (or outside of Prep, if you choose to modify), I advise you to think carefully about 
your workflow and minimize re-running the geocoding on addresses that you have already geocoded...otherwise you'll be 
doing pointless re-geocoding.  

So, geocode once, then save the results and only re-run on the addresses that haven't been geocoded yet :)
I take no responsibility for your geocoding too many addresses and incurring any charges for the service(s) you use.

@author: sbattersby
"""
''' 
Geocoding using the Mapbox geocoding service API
Mapbox geocoding terms of service: https://www.mapbox.com/tos/#geocoding

****Requires a Mapbox token****

	How tokens work: https://docs.mapbox.com/help/how-mapbox-works/access-tokens/
	Create a Mapbox account: https://account.mapbox.com/auth/signup/
'''
import urllib
import json

def Geocode_Mapbox(df):
	MAPBOX_TOKEN = YOUR_API_KEY_GOES_HERE

	for i in range(0, len(df)):
		loc = df.iloc[i]['Address'] + ' ' + df.iloc[i]['City'] + ' '  + df.iloc[i]['State'] + ' ' + str(df.iloc[i]['Zip'])

		# reformat location string for URL
		loc = loc.replace(' ', '+')
		geocode_url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/' + loc + '.json?access_token=' + MAPBOX_TOKEN	
		req = urllib.request.Request(geocode_url)
		r = urllib.request.urlopen(req)
		req_body = r.read()

		j = json.loads(req_body)

		feature = j['features'][0]
		# print(feature)
		if 'accuracy' in feature['properties']:
			df.set_value(i, 'accuracy', feature['properties']['accuracy'])
		if 'center' in feature:
			df.set_value(i, 'Longitude', feature['center'][0])
			df.set_value(i, 'Latitude', feature['center'][1])
			print(i, feature['center'][0],feature['center'][1] )


	return df
