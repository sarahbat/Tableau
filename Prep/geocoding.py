# -*- coding: utf-8 -*-
"""
Created on 7/18/19

Demo of geocoding to convert address strings to lat/lon as part of a Tableau Prep workflow

TODO: Add additional geocoding service options

TODO: Edit so that if there is already a lat/lon value it doesn't need to re-geocode theoretically 
in the prep workflow you would just want to refresh the new locations and not keep re-running 
things you already know

@author: sbattersby
"""

import urllib
import json


def Geocode_Mapbox(df):
MAPBOX_TOKEN = USE_YOUR_OWN_TOKEN!

df['location'] = df['Address'] + ' ' \
                + df['City'] + ' '  \
                + df['State'] + ' ' \
                + df['Zip'].map(str)
                
# reformat location string for URL
df['location'] = df['location'].str.replace(' ', '%20')

df['accuracy'] = 'accuracy goes here'
df['Longitude'] = -99.99
df['Latitude'] = -99.99

for row in df.head().itertuples():
   geocode_url = 'https://api.mapbox.com/geocoding/v5/mapbox.places/' + row.location + '.json?access_token=' + MAPBOX_TOKEN 
   req = urllib.request.Request(geocode_url)
   r = urllib.request.urlopen(req)
   req_body = r.read()
   
   j = json.loads(req_body)
   feature = j['features'][0]
   df.set_value(row.Index, 'accuracy', feature['properties']['accuracy'])
   df.set_value(row.Index, 'Longitude', feature['center'][0])
   df.set_value(row.Index, 'Latitude', feature['center'][1])
return df
