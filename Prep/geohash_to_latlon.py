# -*- coding: utf-8 -*-
"""
Created on 7/29/19

Demo of geohash to lat/lon conversion

requires pygeohash library

@author: sbattersby
"""

import pygeohash as pgh

def Get_LatLon(df):
	for i in range(0, len(df)):
		latLon = pgh.decode(df.iloc[i]['geohash'])
		df.set_value(i, 'Latitude', latLon[0])
		df.set_value(i, 'Longitude', latLon[1])

	return df

'''
Use get_output_schema() to define the schema you plan to return to Tableau Prep
This allows you to return a dataframe that has new fields 
The other option would be to just add the fields in to your data before running the script and comment
out the function below

Do whatever is easiest - if you have a lot of fields in your original table and you want to keep
them all, it's probably easiest to just delete this part of the script.
'''

def get_output_schema():
	return pd.DataFrame({
		'geohash'	: prep_string(),
		'Latitude' 	: prep_decimal(),
		'Longitude' 	: prep_decimal()
		})
