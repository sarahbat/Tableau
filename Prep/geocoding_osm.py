
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
Geocoding using the Open Street Map geocoding service
OSM License info: https://wiki.osmfoundation.org/wiki/Licence

Note that the return from the OSM service is XML, not JSON like the other services used in these examples

'''
import xml.etree.ElementTree as ET
import urllib

def Geocode_OSM(df):

	for i in range(0, len(df)):
		loc = df.iloc[i]['Address'] + ' ' + df.iloc[i]['City'] + ' '  + df.iloc[i]['State'] + ' ' + str(df.iloc[i]['Zip'])

		# reformat location string for URL
		loc = loc.replace(' ', '+')

		geocode_url = 'https://nominatim.openstreetmap.org/search?q=' + loc + '&format=xml&polygon=1&addressdetails=1'

		req = urllib.request.Request(geocode_url)
		r = urllib.request.urlopen(req)
		req_body = r.read()
	    
		root = ET.fromstring(req_body)
		print(i)
		if len(root.getchildren()) >= 1:
			df.set_value(i, 'Longitude', root.find('./place').attrib['lon'])
			df.set_value(i, 'Latitude', root.find('./place').attrib['lat'])
			df.set_value(i, 'Accuracy', 'OSM doesn\'t list accuracy values')
		

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
