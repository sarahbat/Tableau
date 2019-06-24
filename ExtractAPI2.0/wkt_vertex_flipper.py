# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 08:48:15 2019

One super WKT vertex flipper ('Wicked vertex flipper') for Jonathan Drummey

Reverse vertices in a single WKT polygon string so that vertex ordering is in line with
that expected in Tableau (SQL Server semantic)

Should work with polygons with interior rings

Should check WKT type and treat accordingly

@author: sbattersby
"""
from shapely.geometry import Polygon, MultiPolygon

'''
Make array of inner ring polygons with reversed coordinates

Input: Shapely geometry, number of interior rings to peruse
Output: array of interior ring polygons with reversed vertex ordering
'''
def makeInnerRingArray(geom):
    innerRingPolys = []
    innerRingCount = len(geom.interiors)
    for i in range(0, innerRingCount):
        coords = geom.interiors[i].coords[:]
        coordsReverse = coords[::-1]
        # polyReverse = Polygon(coordsReverse)
        innerRingPolys.append(coordsReverse)
    return innerRingPolys

'''
Reverses the vertex ordering in WKT Polygon and MultiPolygon
Should ignore Point, MultiPoint, LineString, MultiLineString if input

Input: One shapely geometry 
Output: wkt string with reversed vertex ordering
'''
def reverse_wkt_string(geom, opt_verbose=False):
    if geom.type == 'Polygon':
        # deal with interior rings
        # did not test with multiple interior rings...
        try:
            innerRingPolys = makeInnerRingArray(geom)
            makeInnerRingArray(geom)
        except: 
            pass # no inner ring; move on...
        
        coords = geom.exterior.coords[:]
        coordsReverse = coords[::-1]
        # Write with any inner ring / holes
        polyReverse = Polygon(coordsReverse, innerRingPolys)
        
        if opt_verbose == True:
            print('polygon:')
            print(polyReverse)                
        return polyReverse

    elif geom.type == 'MultiPolygon':
        polygonCount = len(geom)
        polyArray = []
        # deal with interior rings
        # did not test with multiple interior rings...
        for i in range(0, polygonCount):
            innerRingPolys = []
            try:
                innerRingPolys = makeInnerRingArray(geom[i])
            except: 
                pass # no inner ring
            
            coords = geom[i].exterior.coords[:]
            coordsReverse = coords[::-1]
            polyArray.append(Polygon(coordsReverse, innerRingPolys))
            multipolyReverse = MultiPolygon(polyArray)
        if opt_verbose == True:
            print('multipolygon:')
            print(multipolyReverse)
        return multipolyReverse
        
    else: 
        # Not a Polygon or MultiPolygon, return original geometry
        print('not a polygon or multipolygon')
        return geom
    
    return 0


