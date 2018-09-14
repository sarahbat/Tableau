# -*- coding: utf-8 -*-

###
# @sarahbat (Sarah Battersby)
#
# Process NOAA NHC shapefiles and combine with US Census tract-level data in SQL Server 
# Is a setup for working with the data in Tableau for examining social impacts of hurricanes
#
# CAVEAT: Currently hard codes many aspects of my own SQL Server Express setup (and, no, you don't get my password) 
#         and has room for improvement to the workflow to take commandline inputs and do some initial process when
#         when the NOAA data is in a wonky multi-part format.
#
# Python = 2.7
###

# TODO set up to run from commandline - input_shp, finalOutput_table, database_name
# TODO can I go singlepart to multipart easily for the storm polys in SQL Server? Otherwise can take a long time to process
# TODO scrape "latest" file from https://www.nhc.noaa.gov/refresh/graphics_at1+shtml/152247.shtml?hwind120#wcontents
    # need to check...doesn't always seem to be single-storm specific, so haven't implemented yet

import pyodbc
import os
import subprocess
import sys


def main(input_shp, db_name, epsg_code):
    input_data = get_data(input_shp)
    ogr_2_sql(input_data, epsg_code, db_name)
    process_sql(db_name, input_data)

    print 'Data ready for Tableau!'


def get_data(input_shp):
    # TODO scrape from https://www.nhc.noaa.gov/refresh/graphics_at1+shtml/152247.shtml?hwind120#wcontents
    # https://www.nhc.noaa.gov/gis/forecast/archive/wsp_120hr5km_latest.zip
    if input_shp[-4:] != '.shp':
        print 'Input file is not a shapefile, exiting...'
        exit()
    if os.path.dirname(input_shp) == '':
        # only file name included, assume current directory
        dir = os.getcwd()
        input_shp = dir + input_shp

    return input_shp


# Assumes SQL Server Express running locally...not going to make super-generic right now...
def ogr_2_sql(input_shp, epsg_code, db_name):
    import_ogr = 'ogr2ogr -f "MSSQLSpatial" "MSSQL:server=localhost\SQLEXPRESS;Database=' + db_name \
                + ';Trusted_Connection=yes" '
    import_ogr += '"' + input_shp + '" '
    import_ogr += '-a_srs "EPSG:'
    import_ogr += epsg_code
    import_ogr += '"'

    subprocess.call(import_ogr)

    
# Run all SQL processing to combine Census and NOAA datasets
# Assumes that Census tract-level data is already in your database
def process_sql(db_name, input_data):
    input_shp_name = os.path.basename(input_data)[:-4]  # strip off .shp

    # Connect to server
    con = pyodbc.connect(
                         driver='{SQL Server}',
                         server='localhost\SQLEXPRESS',
                         Trusted_Connection='yes',
                         database=db_name)

    cursor = con.cursor()

    sql_str = "alter table " + db_name + ".dbo.[" + input_shp_name + "]"
    sql_str += " add ogr_geography geography"
    cursor.execute(sql_str)
    con.commit()
    print 'geography added...'

    sql_str = "update " + db_name + ".dbo.[" + input_shp_name + "]"
    sql_str += "set ogr_geography = "
    sql_str += "ogr_geometry.MakeValid()."
    sql_str += "STUnion(ogr_geometry.MakeValid()."
    sql_str += "STStartPoint()).STAsText();"
    cursor.execute(sql_str)
    con.commit()
    print 'geography calculated...'

    sql_str = "create spatial index SIndx_" + input_shp_name + "_geom "
    sql_str += "on " + db_name + ".dbo.[" + input_shp_name + "](ogr_geometry) "
    sql_str += "with (Bounding_Box = (0,0,500,200));"
    cursor.execute(sql_str)
    con.commit()
    print 'spatial index created...'

    sql_str = "select  t.ogr_fid as fid_tract, t.ogr_geography as geog_tract, t.geoid10 as geoid_tract, "
    sql_str += "s.ogr_fid as fid_storm, s.ogr_geography as geog_storm, s.percentage as percentage_storm, "
    sql_str += "t.ogr_geography.STIntersection(s.ogr_geography) as geog_tract_partial, "
    sql_str += "t.ogr_geography.STArea() * 3.86102159E-7 as area_tract_whole_mi2, "
    sql_str += "t.ogr_geography.STIntersection(s.ogr_geography).STArea() * 3.86102159E-7 as area_tract_partial_mi2 "
    sql_str += "into " + db_name + ".dbo.[" + input_shp_name + "_tract] "
    sql_str += "from hurricane.dbo.tract_2010census_dp1  as t "
    sql_str += "right join "
    sql_str += db_name + ".dbo.[" + input_shp_name + "] as s "
    sql_str += "on s.ogr_geography.STIntersects(t.ogr_geography) = 1; "

    cursor.execute(sql_str)
    con.commit()
    print 'intersection complete...'

    cursor.close()
    del cursor
    con.close()


# Currently assumes SHP has been downloaded and processed
# Shp should be multipart with just the storm of interest included (NOAA includes all global storms by default)
if __name__ == "__main__":
    # TODO add in inputs from command line...otherwise use some defaults
    # print "This is the name of the script: ", sys.argv[0]
    # print "Number of arguments: ", len(sys.argv)
    # print "The arguments are: ", str(sys.argv)

    input_shp = "C:\\Users\\sbattersby\\Downloads\\Florence\\2018091218_wsp64knt120hr_5km_florence.shp"
    epsg_code = "4326"
    database_name = "hurricane"

    main(input_shp, database_name, epsg_code)
