# -*- coding: utf-8 -*-
"""
Created on 7/30/19

Demo of what3words to lat/lon
requires what3words library
@author: sbattersby

"""

import what3words

def Get_LatLon(df):

        W3W_API_KEY = 'YOUR_API_KEY_GOES_HERE'
        g = what3words.Geocoder(W3W_API_KEY)

        for i in range(0, len(df)):
                # assumes you have all of the words in one column (e.g., 'subsides.oilman.wildcard')
                # if you have them in separate columns, you'll need to concatenate with period between
                # prior to converting to coordinates
                res = g.convert_to_coordinates(df.iloc[i]['w3w'])

                df.set_value(i, 'Latitude', res['coordinates']['lat'])
                df.set_value(i, 'Longitude', res['coordinates']['lng'])    

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
                'w3w'         : prep_string(),
                'Latitude'    : prep_decimal(),
                'Longitude'   : prep_decimal(),
                'lat'         : prep_decimal(),
                'long'        : prep_decimal()
                })
