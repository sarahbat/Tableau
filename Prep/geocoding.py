# -*- coding: utf-8 -*-
"""
Created on 7/18/19

Demo of geocoding to convert address strings to lat/lon as part of a Tableau Prep workflow

Assumes that your address is coming in from separate fields of Address, City, State, Zip...modify the query to fit 
whatever you are using for input.  All you need to do it mush everythign together into a single string to pass
to the geocoding service.

Also assumes that you have a file with fields for Latitude, Longitude, and accuracy for the geocoding output 
(I added those with a step in my Tableau Prep workflow, then ran the script)

Currently provides options for using Google API, Mapbox API, and Open Street Map
Please pay attention to licensing restrictions on whatever service you use

For Google and Mapbox you will need an API key.  Currently there are free tiers for licensing that will give you ability to 
geocode a decent number of records.

When using this with Tableau Prep (or outside of Prep, if you choose to modify), think carefully about your workflow and 
minimize re-running the geocoding on addresses that you have already geocoded...otherwise you'll be doing pointless re-geocoding.  
So, geocode once, then save the results and only re-run on the addresses that haven't been geocoded yet :)

I take no responsibility for your geocoding too many addresses and incurring any charges for the service(s) you use.

@author: sbattersby
"""

import urllib
import json
import xml.etree.ElementTree as ET

''' 
Geocoding using the Mapbox geocoding service API
Mapbox geocoding terms of service: https://www.mapbox.com/tos/#geocoding

****Requires a Mapbox token****

	How tokens work: https://docs.mapbox.com/help/how-mapbox-works/access-tokens/
	Create a Mapbox account: https://account.mapbox.com/auth/signup/
'''
def Geocode_Mapbox(df):
	MAPBOX_TOKEN = PUT_YOUR_MAPBOX_API_KEY_HERE

	df['location'] = df['Address'] + ' ' \
                + df['City'] + ' '  \
                + df['State'] + ' ' \
                + df['Zip'].map(str)
                
	# reformat location string for URL
	df['location'] = df['location'].str.replace(' ', '+')

	df['accuracy'] = 'accuracy goes here'
	df['Longitude'] = -99.99
	df['Latitude'] = -99.99

	for row in df.head().itertuples():
	    geocode_url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/' + row.location + '.json?access_token=' + MAPBOX_TOKEN	
	    req = urllib.request.Request(geocode_url)
	    r = urllib.request.urlopen(req)
	    req_body = r.read()
	    
	    j = json.loads(req_body)
	    # return for first match listed
	    feature = j['features'][0]
	    df.set_value(row.Index, 'accuracy', feature['properties']['accuracy'])
	    df.set_value(row.Index, 'Longitude', feature['center'][0])
	    df.set_value(row.Index, 'Latitude', feature['center'][1])
	return df



''' 
Geocoding using the Google Maps geocoding service API
Mapbox geocoding terms of service: https://developers.google.com/maps/documentation/geocoding/policies

****Requires a Google API Key****

	Get an API key: https://developers.google.com/maps/documentation/javascript/get-api-key

Note: If your application displays data from the Geocoding API on a page or view that does not also display 
a Google Map, you must show a Powered by Google logo with that data. For example, if your application 
displays Geocoding API data on one tab, and a Google Map with that data on another tab, the first tab 
must show the Powered by Google logo.
'''
def Geocode_Google(df):
	GOOGLE_API_KEY = PUT_YOUR_GOOGLE_API_KEY_HERE
	df['location'] = df['Address'] + ' ' \
                + df['City'] + ' '  \
                + df['State'] + ' ' \
                + df['Zip'].map(str)
                
	# reformat location string for URL
	df['location'] = df['location'].str.replace(' ', '+')

	df['accuracy'] = 'accuracy goes here'
	df['Longitude'] = -99.99
	df['Latitude'] = -99.99

	for row in df.head().itertuples():
	    geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + row.location + '&key=' + GOOGLE_API_KEY

	    req = urllib.request.Request(geocode_url)
	    r = urllib.request.urlopen(req)
	    req_body = r.read()
	    
	    j = json.loads(req_body)
	    # return for first match listed
	    df.set_value(row.Index, 'accuracy', j['results'][0]['geometry']['location_type'])
	    df.set_value(row.Index, 'Longitude', j['results'][0]['geometry']['location']['lng'])
	    df.set_value(row.Index, 'Latitude', j['results'][0]['geometry']['location']['lat'])
	return df


''' 
Geocoding using the Open Street Map geocoding service
OSM License info: https://wiki.osmfoundation.org/wiki/Licence

Note that the return from the OSM service is XML, not JSON like the other services used in these examples

'''
def Geocode_OSM(df):
	df['location'] = df['Address'] + ' ' \
                + df['City'] + ' '  \
                + df['State'] + ' ' \
                + df['Zip'].map(str)
                
	# reformat location string for URL
	df['location'] = df['location'].str.replace(' ', '+')

	df['accuracy'] = 'accuracy goes here'
	df['Longitude'] = -99.99
	df['Latitude'] = -99.99

	for row in df.head().itertuples():
	    geocode_url = 'https://nominatim.openstreetmap.org/search?q=' + row.location + '&format=xml&polygon=1&addressdetails=1'

	    req = urllib.request.Request(geocode_url)
	    r = urllib.request.urlopen(req)
	    req_body = r.read()

	    # parse the XML string, hopefully only one place in the return :)
	    root = ET.fromstring(req_body)
	    df.set_value(row.Index, 'Longitude', root.find('./place').attrib['lon'])
	    df.set_value(row.Index, 'Latitude', root.find('./place').attrib['lat'])
	    df.set_value(row.Index, 'accuracy', 'OSM doesn\'t list accuracy values')

	return df
