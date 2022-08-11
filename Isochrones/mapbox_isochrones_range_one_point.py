'''
Generate multiple isochrones (travel time polygons) around a *single* point location at specified distances in a range
For instance, 1 - 60 min. walking distances around a single point location, in increments of 1 minute (so, 60 polygons)
Write result to a .hyper file for use in Tableau

Isochrones will go in separate ROWS for each distance/profile combination.  

This code is written for understandability by non-coders, as opposed to efficient
Edit as you see fit and as is relevant for your needs.

Things you will edit:
* lat / lng - put in the point location that you're interested in
* path_to_hyper - where do you want to save the output .hyper
    the .hyper is for use in Tableau, if you want something else, edit the code so the output goes somewhere else
* profiles - put in the "profiles" that you want for isochrones (walking, cycling, and/or driving)
* min_minutes, max_minutes, dist_step_size - shortest distance of interest, longest, and what step for iteration
* Either hard code your Mapbox API key (not recommended) or point to the relevant place where you keep it hidden


Notes
* Mapbox API will take up to 4 isochrone distances in a single call.
* I'm just making a separate call for each instead of bundling into 4 distance chunks


Have at it...
-Sarah Battersby (sarahbat@gmail.com)
'''
import geopandas as gpd
from shapely.geometry import Point
import os
import requests
import json

# You can hard code your Mapbox API key if you really want, but I'd recommend not doing that
# I'm not giving you my Mapbox API key :)
mb_token = os.environ.get("MAPBOX_API_KEY")

# input location as lat and lng
# I'm not going out of my way to be flexible and delightful, just aiming for readable and functional
lat = 47.64959
lng = -122.34786

# output for the .hyper file
path_to_hyper = r"your_output_file.hyper"

# Read the point data into a GeoPandas geodataframe (gdf)
# This is just a nice way to input the data into a gdf (and then store the isochrone polygons as spatial data)

d = {'pointGeometry': [Point(lat, lng)], 'Isochrone': [None], 'Distance': [None]}
gdf = gpd.GeoDataFrame(d)
gdf.set_geometry('pointGeometry', 4326)

# What isochrone profiles do you want to collect? (walking, driving, and/or cycling)
profiles = ["walking", "driving"]
# What distance?  Let's define a min, max, and step size!
min_minutes = 5
max_minutes = 10
dist_step_size = 1

# make string of minutes
min_string = str(min_minutes)
for minute in range(min_minutes+dist_step_size, max_minutes, dist_step_size):
    min_string = f'{min_string},{minute}'

# Tap into the awesome Mapbox API and grab isochrones around _each_ point in your dataset
# make the isochrones for every combination of profile and minutes (distance) for each point
results = []
row = 0
for profile in profiles:
    for minute in range(min_minutes, max_minutes, dist_step_size):
        print(f"Collecting isochrones for {minute} minutes {profile}...")
        iso_url = f"https://api.mapbox.com/isochrone/v1/mapbox/{profile}/{lng},{lat}?contours_minutes={minute}&polygons=true&access_token={mb_token}"

        r = requests.get(iso_url)
        json.dumps(r.json())
        if r.status_code == 200:
            poly_gdf = gpd.read_file(json.dumps(r.json()), driver='GeoJSON')
            results.append({
                'lat': lat,
                'lng': lng,
                'point': Point(lng, lat),
                'isochrone': poly_gdf.iloc[0]['geometry'],
                'distance': minute,
                'profile': profile
            })


        else:
            print(f"{r.status_code} code was returned for element {i}, profile {profile}")

        row = row + 1

    # make gdf and set cols as geometry
    gdf = gpd.GeoDataFrame(results)
    gdf = gdf.set_geometry('isochrone')
    gdf = gdf.set_geometry('point')

# Convert the resulting isochrones into a .hyper file for easy use in Tableau
# based on:
# https://help.tableau.com/current/api/hyper_api/en-us/docs/hyper_api_geodata.html#example-code-using-the-inserter
from tableauhyperapi import Connection, HyperProcess, SqlType, TableDefinition, \
    escape_name, Telemetry, Inserter, CreateMode, TableName

# make a copy of the gdf - we will convert the geom to wkt and store in this copy
# probably really don't need to make a copy; could prob just overwrite the geom in the original with WKT
gdf_copy = gdf.copy()

with HyperProcess(Telemetry.SEND_USAGE_DATA_TO_TABLEAU, 'myapp' ) as hyper:
    print("The HyperProcess has started.")

    with Connection(hyper.endpoint, path_to_hyper, CreateMode.CREATE_AND_REPLACE) as connection:
        print("The connection to the Hyper file is open.")

        # dynamically make geo_table definition from the geodataframe (gdf)
        connection.catalog.create_schema('Extract')
        gdf_table = TableDefinition(TableName('Extract', 'Extract'), [])
        inserter_definition = []
        column_mappings = []
        # load in the fields
        cols = gdf.columns

        # walk through gdf and add column based on data type
        # while we're here, let's make sure any geometries are converted to WKT
        for col in cols:
            col_dtype = gdf[col].dtype
            sql_type = None
            inserter_name = col
            col_map_name = col
            if col_dtype == 'O':
                sql_type = inserter_type = SqlType.text()
            if col_dtype == 'int64':
                sql_type = inserter_type = SqlType.int()
            if col_dtype == 'float64':
                sql_type = inserter_type = SqlType.double()
            if col_dtype == 'geometry':
                sql_type = SqlType.geography()
                # for inserter, cols with SqlType.geography() are specified as SqlType.text()
                inserter_type = SqlType.text()
                inserter_name = f'{col}_as_text'
                # Specify the conversion of SqlType.text() to SqlType.geography() using CAST expression in
                # <Inserter.ColumnMapping>. Specify all columns into which data is inserter in Inserter.ColumnMapping
                # list.
                col_map_name = Inserter.ColumnMapping(col, f'CAST({escape_name(f"{col}_as_text")} AS GEOGRAPHY)')
                # make sure the data we're going to write has the spatial as WKT (done in a copy of the gdf)
                gdf_copy[col] = gdf_copy[col].to_wkt().str.encode(encoding='utf-8')

            # actually add the columns to the table
            gdf_table.add_column(col, sql_type)
            # set up inserter
            inserter_definition.append(
                TableDefinition.Column(name=inserter_name, type=inserter_type)
            )
            # set up column mappings
            column_mappings.append(col_map_name)

        connection.catalog.create_table(gdf_table)
        print("The geo_table is defined.")

        # convert gdf to list so we can drop into the .hyper easily
        # NOTE the geometry must be WKT! We converted geometry to WKT above
        gdf_as_list = gdf_copy.to_numpy().tolist()

        with Inserter(connection, gdf_table, column_mappings, inserter_definition=inserter_definition) as inserter:
            inserter.add_rows(rows=gdf_as_list)
            inserter.execute()
        print("The data was added to the table")

    print("The connection to the Hyper extract file is closed.")
print("The HyperProcess has shut down.")
