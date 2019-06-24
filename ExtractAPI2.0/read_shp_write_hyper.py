# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 15:13:08 2019

Demo to read shapefile, reverse vertices, write to Hyper

@author: sbattersby
"""

import geopandas as gpd
import fiona
import wkt_vertex_flipper as wktFlip
from tableausdk import * 
from tableausdk.HyperExtract import *


def main():   
   
    write_shp_to_hyper(
            'd:\\_data\\Seattle\\SPD_Beats_WGS84.shp', # shp location
            'SPD Beats4', # table name
            'd:\\test-seattlePoliceBeats.hyper' # hyper file name
            )
    
    return 0


# Given a shapefile in a geodataframe, grab the schema to write into
# a .hyper file
def get_shp_schema(shpLocation):
    with fiona.open(shpLocation) as f:
        inputSchema = f.schema
    
    return inputSchema['properties']


# Given a shapefile schema, assign the appropriate columns to the hyper schema
# TODO: Check what other data types are caught by fiona in the shapefile dbf
def make_hyper_schema(shpSchema):
    schema = TableDefinition()
    for key in shpSchema:
        colType = shpSchema[key][0:3]
        if (colType == 'str'):
            schema.addColumn(key,   Type.CHAR_STRING)
        if (colType == 'int'):
            schema.addColumn(key,   Type.INTEGER)
        if (colType == 'flo'): # float
            schema.addColumn(key,   Type.DOUBLE)

    # Tack on the spatial at the end - it won't be seen in the other atts
    # from the shapefile dbf
    schema.addColumn('geom',        Type.SPATIAL)
    
    return schema


def write_shp_to_hyper(shpLocation,tableName, hyperOutputLocation):
    gdf = gpd.GeoDataFrame.from_file(shpLocation)
       
    # Prep Hyper extract for data dump
    ExtractAPI.initialize()
    extract = Extract(hyperOutputLocation)
    
    # make Hyper schema - could probably do this with geopandas
    # so that we don't have to open shp twice, but this was easier than
    # reading the helpfiles on geopandas
    shpSchema = get_shp_schema(shpLocation)
    hyperSchema = make_hyper_schema(shpSchema)
    # Make the table and set up the schema
    table = extract.addTable(tableName, hyperSchema)
    
    # Add data to the table
    currentTable = extract.openTable(tableName)
    tableDefn = currentTable.getTableDefinition()
    row = Row(tableDefn)
    
    # TODO: Check what other data types are caught.  Currently just str, int, float
    for i in range(0,len(gdf)):
        colCount = 0
        for key in shpSchema:
            colType = shpSchema[key][0:3]
            if colType == 'str':
                try:
                    row.setCharString(colCount, gdf.iloc[i][key])
                except:
                    row.setCharString(colCount, '-999')
            if colType == 'int':
                row.setInteger(colCount, gdf.iloc[i][key])
            if colType == 'flo':
                row.setDouble(colCount, gdf.iloc[i][key])
            colCount += 1
        geoData = wktFlip.reverse_wkt_string(gdf.iloc[i]['geometry'])
        row.setSpatial(colCount, geoData.wkt.encode('ascii'))

        currentTable.insert(row)
    
    extract.close()
    return 


if __name__ == "__main__":
    main()