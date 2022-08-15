'''
Generate one or more isochrones (travel time polygons) around a *shapefile* of point locations at specified distances and for specified profiles
Write result to a .hyper file for use in Tableau

Isochrones will go in separate COLUMNS for each distance/profile combination.  

This code is written for understandability by non-coders, as opposed to efficient
Edit as you see fit and as is relevant for your needs.

Things you will edit:
* pt_file_loc - where is your point shapefile?
* path_to_hyper - where do you want to save the output .hyper
    the .hyper is for use in Tableau, if you want something else, edit the code so the output goes somewhere else
* profiles - put in the "profiles" that you want for isochrones (walking, cycling, and/or driving)
* minutes - an array of distances.  Put in whatever distances you want.  Pay attention to the Mapbox pricing structure if you're worried about charges...
* Either hard code your Mapbox API key (not recommended) or point to the relevant place where you keep it hidden

Have fun...
-Sarah Battersby 
'''

import geopandas as gpd
import os
import requests
import json

# You can hard code your Mapbox API key if you really want, but I'd recommend not doing that
# I'm not giving you my Mapbox API key :)
mb_token = os.environ.get("MAPBOX_API_KEY")

# input dataset (in this case reading from a shapefile of points)
pt_file_loc = r"your_point_spatial_file.shp"

# output for the .hyper file
path_to_hyper = r"your_output_hyper_file.hyper"

# Read the point data into a GeoPandas geodataframe
# This is just a nice way to input the geometry from shapefile (and then store the isochrone polygons)
pt_data = gpd.read_file(pt_file_loc)

# What isochrone profiles do you want to collect? (walking, driving, and/or cycling
profiles = ["walking", "cycling"]
# What distance?  I've set this up as a single element in an array so that it's easier to add
# additional distances of interest without manipulating the loop that collects the isochrones
minutes = [10]

# Tap into the awesome Mapbox API and grab isochrones around _each_ point in your dataset
# make the isochrones for every combination of profile and minutes (distance) for each point
for profile in profiles:
    for minute in minutes:
        print(f"Collecting isochrones for {minute} minutes {profile}...")
        for i in range(0, len(pt_data)):
            lat = pt_data.iloc[i].geometry.y
            lng = pt_data.iloc[i].geometry.x

            iso_url = f"https://api.mapbox.com/isochrone/v1/mapbox/{profile}/{lng},{lat}?contours_minutes={minute}&polygons=true&access_token={mb_token}"

            r = requests.get(iso_url)
            json.dumps(r.json())
            if r.status_code == 200:
                poly_gdf = gpd.read_file(json.dumps(r.json()), driver='GeoJSON')
                pt_data.loc[[i], f'{profile}_{minute}'] = poly_gdf.iloc[0]['geometry']
            else:
                print(f"{r.status_code} code was returned for element {i}, profile {profile}")

        # set col as geometry
        pt_data = pt_data.set_geometry(f'{profile}_{minute}')

# Convert the resulting isochrones into a .hyper file for easy use in Tableau
# based on:
# https://help.tableau.com/current/api/hyper_api/en-us/docs/hyper_api_geodata.html#example-code-using-the-inserter
from tableauhyperapi import Connection, HyperProcess, SqlType, TableDefinition, \
    escape_name, Telemetry, Inserter, CreateMode, TableName

# make a copy of the gdf - we will convert the geom to wkt and store in this copy
# probably really don't need to make a copy; could prob just overwrite the geom in the original with WKT
pt_data_copy = pt_data.copy()

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
        cols = pt_data.columns

        # walk through gdf and add column based on data type
        # while we're here, let's make sure any geometries are converted to WKT
        for col in cols:
            col_dtype = pt_data[col].dtype
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
                pt_data_copy[col] = pt_data_copy[col].to_wkt().str.encode(encoding='utf-8')

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
        gdf_as_list = pt_data_copy.to_numpy().tolist()

        with Inserter(connection, gdf_table, column_mappings, inserter_definition=inserter_definition) as inserter:
            inserter.add_rows(rows=gdf_as_list)
            inserter.execute()
        print("The data was added to the table")

    print("The connection to the Hyper extract file is closed.")
print("The HyperProcess has shut down.")
