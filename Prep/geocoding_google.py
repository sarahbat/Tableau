
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

@author: sarahbat
"""

''' 
Geocoding using the Google Maps geocoding service API
Google geocoding terms of service: https://developers.google.com/maps/documentation/geocoding/policies

****Requires a Google API Key****

	Get an API key: https://developers.google.com/maps/documentation/javascript/get-api-key

Note: If your application displays data from the Geocoding API on a page or view that does not also display 
a Google Map, you must show a Powered by Google logo with that data. For example, if your application 
displays Geocoding API data on one tab, and a Google Map with that data on another tab, the first tab 
must show the Powered by Google logo.
'''

import urllib
import json

def Geocode_Google(df):
	GOOGLE_API_KEY = YOUR_API_KEY_GOES_HERE 
	
	for i in range(0, len(df)):
		loc = df.iloc[i]['Address'] + ' ' + df.iloc[i]['City'] + ' '  + df.iloc[i]['State'] + ' ' + str(df.iloc[i]['Zip'])

		# reformat location string for URL
		loc = loc.replace(' ', '+')

		geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + loc + '&key=' + GOOGLE_API_KEY

		req = urllib.request.Request(geocode_url)
		r = urllib.request.urlopen(req)
		req_body = r.read()
	    
		j = json.loads(req_body)
		# return for first match listed
		if 'location_type' in j['results'][0]['geometry']:
			df.set_value(i, 'Accuracy', j['results'][0]['geometry']['location_type'])
		if 'location' in j['results'][0]['geometry']:
			df.set_value(i, 'Longitude', j['results'][0]['geometry']['location']['lng'])
			df.set_value(i, 'Latitude', j['results'][0]['geometry']['location']['lat'])
	return df


'''
Use get_output_schema() to define the schema you plan to return to Tableau Prep
This allows you to return a dataframe that has new fields 

The other option would be to just add the fields in to your data before running the script

Do whatever is easiest - if you have a lot of fields in your original table and you want to keep
them all, it's probably easiest to just delete this part of the script.
'''

'''
def get_output_schema():
	return pd.DataFrame({
		'Accuracy' 	: prep_string(),
		'Latitude' 	: prep_decimal(),
		'Longitude' 	: prep_decimal(),
		'Address' 	: prep_string(),
		'City'		: prep_string(),
		'State'		: prep_string(),
		'Zip'		: prep_string(),
		'Lat'		: prep_decimal(),
		'Lng'		: prep_decimal()
		})
'''
