# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 15:09:17 2019

@author: sbattersby
"""
import shapely.wkt
import wkt_vertex_flipper

def test(wkt_string):
    geom = shapely.wkt.loads(wkt_string)
    print('Testing ' + geom.type)
    reverse_wkt_string(geom, opt_verbose = True)


def run_test():
    # Test WKT strings
    wkt_point =                "POINT (30 10)"
    wkt_multipoint =           "MULTIPOINT (10 40, 40 30, 20 20, 30 10)"
    wkt_linestring =           "LINESTRING (30 10, 10 30, 40 40)"
    wkt_multilinestring =      "MULTILINESTRING ((10 10, 20 20, 10 40), \
                                    (40 40, 30 30, 40 20, 30 10))"
    wkt_polygon =              "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))"
    wkt_polygon_hole =         "POLYGON ((35 10, 45 45, 15 40, 10 20, 35 10), \
                                    (20 30, 35 35, 30 20, 20 30))"
    wkt_multipolygon =         "MULTIPOLYGON (((30 20, 45 40, 10 40, 30 20)), \
                                    ((15 5, 40 10, 10 20, 5 10, 15 5)))"
    wkt_multipolygon_hole =    "MULTIPOLYGON (((40 40, 20 45, 45 30, 40 40)), \
                                    ((20 35, 10 30, 10 10, 30 5, 45 20, 20 35), \
                                     (30 20, 20 15, 20 25, 30 20)))"
    
    test(wkt_point)
    test(wkt_multipoint)
    test(wkt_linestring)
    test(wkt_multilinestring)
    test(wkt_polygon)
    test(wkt_polygon_hole)
    test(wkt_multipolygon)
    test(wkt_multipolygon_hole)