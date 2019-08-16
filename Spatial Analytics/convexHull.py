# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:48:41 2019

Python method for making convex hulls

This is a demo script in response to a Tableau Forums question 

https://community.tableau.com/thread/313129

"I would like to create a spatial file that will create custom polygons 
of the outline of each cluster of customers."

@author: sarahbat
"""


import geopandas as gpd
from shapely.geometry import Point

CSV_LOCATION = r'C:\Users\sbattersby\Downloads\testspacial.csv'
SHP_OUTPUT_LOCATION = r'C:\temp\shpOutput.shp'
GROUP_FIELD = 'Actual RouteID' # the field that defines how points will be grouped
LATITUDE_FIELD = 'Latitude' # the names for the fields with your x,y coordinates
LONGITUDE_FIELD = 'Longitude'

# read in the csv
gdf = gpd.read_file(CSV_LOCATION)

# make point geometry (skip rows with null coordinates)
for i in range(0, len(gdf)):
    x = gdf.iloc[i][LONGITUDE_FIELD]
    y = gdf.iloc[i][LATITUDE_FIELD]
    
    if x == 'NULL' or y == 'NULL':
        continue
    else:
        gdf.at[i, 'geometry'] = Point(float(x), float(y))

# clean so that the null point geometries are removed
# the last step left those rows in, but didn't make Points for them
gdf_clean = gdf[gdf.geometry.type == 'Point']

# dissolve the points into multipoints based on attribute
dis = gdf_clean.dissolve(by=GROUP_FIELD)

# make a new geoDataFrame to hold the convex hull polygons
gdf_hulls = gpd.GeoDataFrame()

# make convex hulls for each group
for i in range(0, len(dis)):
    gdf_hulls.at[i, 'geometry'] = dis.iloc[i].geometry.convex_hull
    gdf_hulls.at[i, GROUP_FIELD] = dis.iloc[i].name
    
# write hulls to shapefile
gdf_hulls.to_file(SHP_OUTPUT_LOCATION)
