# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 14:17:29 2019

Exploring Moran's I and Getis Ord General G

I'm curious about the impact of neighborhood definition...

@author: sbattersby
"""


import pysal
import geopandas as gpd
import numpy as np


# Load data (shapefile so it's easy to build polygon weights matrix)
gdf = gpd.read_file(r'D:\_data\Census\County\tl_2017_us_county.shp')
crs = gdf.crs
gdf_atts = gpd.read_file(r'c:\temp\obesity_data_simple.csv')


# drop the random geometry column in the csv
gdf_atts = gdf_atts.drop(['geometry'], axis=1)
gdf_atts = gdf_atts.rename(columns={'FIPS':'GEOID'})

# add leading 0 to FIPS in the attribute table (stupid CSV)
for i in range(0, len(gdf_atts)):
    if len(gdf_atts.iloc[i].GEOID) == 4:
        gdf_atts.at[i, 'GEOID'] = '0' + gdf_atts.iloc[i].GEOID
    # else do nothing, just keep original value

# merge the attributes to the shapes
gdf = gdf.merge(gdf_atts, on='GEOID')

# update PCT_04 to float64 so that the binning works
gdf = gdf.astype({'PCT_04': 'float64'})

# make sure geometry is active (something weird happens with the merge)
gdf = gdf.set_geometry('geometry')
gdf.crs = crs # reassign crs

# data = pysal.lib.io.open(r'c:\temp\pysaltests\data\texas.shp')
ATTRIBUTE = 'PCT_04'

# make weights matrix
# use GEOID for key, note that the addition of id field is different
# in different weights calcualtion methods
wq = pysal.lib.weights.Queen.from_dataframe(gdf, idVariable='GEOID')
wr = pysal.lib.weights.Rook.from_dataframe(gdf, idVariable='GEOID')
wknn3 = pysal.lib.weights.KNN.from_dataframe(gdf, k=3, ids=gdf.GEOID)

# do with projected coordinate system
gdf_prj = gdf.to_crs({'init': 'epsg:2163'})
wknn3_prj = pysal.lib.weights.KNN.from_dataframe(gdf_prj, k=3, ids=gdf.GEOID)

# minimum threshold distance-based (max nearest neighbor distance)
# function works with points not polys, so base on centroid
centroids = gdf_prj['geometry'].centroid
centroidList = []
for c in centroids:
    centroidList.append((c.x, c.y))
threshold = pysal.lib.weights.min_threshold_distance(centroidList)
wmtd = pysal.lib.weights.DistanceBand(centroidList, threshold, ids=gdf.GEOID)


wq.transform = 'r' # row standardize
wr.transform = 'r'
wknn3.transform = 'r'
wknn3_prj.transform = 'r'
wmtd.transform = 'r'


# Calculate spatial lag for each weigts matrix

# attribute similarity - calculate spatial lag
y = gdf[ATTRIBUTE]
ylag_q = pysal.lib.weights.lag_spatial(wq, y)
ylag_r = pysal.lib.weights.lag_spatial(wr, y)
ylag_knn3 = pysal.lib.weights.lag_spatial(wknn3, y)
ylag_knn3_prj = pysal.lib.weights.lag_spatial(wknn3_prj, y)
ylag_wmtd = pysal.lib.weights.lag_spatial(wmtd, y)

# Moran's I (global)
np.random.seed(12345)
mi_q = pysal.explore.esda.moran.Moran(y, wq)
mi_r = pysal.explore.esda.moran.Moran(y, wr)
mi_knn3 = pysal.explore.esda.moran.Moran(y, wknn3)
mi_knn3_prj = pysal.explore.esda.moran.Moran(y, wknn3_prj)
mi_wmtd = pysal.explore.esda.moran.Moran(y, wmtd)

# Moran's I (local)
li_q = pysal.explore.esda.Moran_Local(y, wq)
li_r = pysal.explore.esda.Moran_Local(y, wr)
li_knn3 = pysal.explore.esda.Moran_Local(y, wknn3)
li_knn3_prj = pysal.explore.esda.Moran_Local(y, wknn3_prj)
li_wmtd = pysal.explore.esda.Moran_Local(y, wmtd)

# Write results from Moran's I to GDF and save as SHP
# Ylag
gdf['ylag_q'] = ylag_q
gdf['ylag_r'] = ylag_r
gdf['ylag_knn3'] = ylag_knn3
gdf['ylag_knn3_prj'] = ylag_knn3_prj
gdf['ylag_wmtd'] = ylag_wmtd

# quadrant
gdf['li_q'] =  li_q.q
gdf['li_r'] =  li_r.q
gdf['li_knn3'] =  li_knn3.q
gdf['li_knn3_prj'] =  li_knn3_prj.q
gdf['li_wmtd'] = li_wmtd.q

# I values
gdf['li_Is_q']= li_q.Is
gdf['li_Is_r']= li_r.Is
gdf['li_Is_knn3']= li_knn3.Is
gdf['li_Is_knn3_prj']= li_knn3_prj.Is
gdf['li_Is_wmtd'] = li_wmtd.Is

# simulated p value
gdf['li_psim_q'] = li_q.p_sim
gdf['li_psim_r'] = li_r.p_sim
gdf['li_psim_knn3'] = li_knn3.p_sim
gdf['li_psim_knn3_prj'] = li_knn3_prj.p_sim
gdf['li_psim_wmtd'] = li_wmtd.p_sim


# Getis Ord (General G) local - queen only so far
g = pysal.explore.esda.getisord.G(y, wq)
glocal = pysal.explore.esda.getisord.G_Local(y, wq)

gdf['glocal_zs'] = glocal.Zs # result z statistics
gdf['glocal_psim'] = glocal.p_sim # p values for sims


# Write to csv for Tableau-ing
gdf.to_csv(r'c:\temp\moran_weightIteration.csv')
