# This code will process the yearly property sales data files from the NSW government website.
# The file format changed in 2001, so this assumes only data after that year.
#
# Notes on structuring your data
# There are two different formats for the downloaded data, this script will deal with both
# 2001-2014: yearly zip file with non-zipped folders inside, each containing some .dat files
# 2015-2023: yearly zip file with zipped files inside, with each of those then containing folders with .dat
#
# Notes:
# - This will write a Tableau .hyper file at the end with all of the data.  If you want a .csv, export the Pandas dataframe
#
# Ken Flerlage has another nice variant on this problem here: https://github.com/flerlagekr/NSW-Property-Sales/blob/main/Combine.py

import pandas as pd
from zipfile import ZipFile

### Big dataset from Mark T. with differing file structures (2001-2014 are same; 2015-2023 are same)
zip_of_zips_loc = r'C:\Users\sarah\Downloads\wetransfer_2002-zip_2023-02-08_2104.zip'

# column names from the Current_Property_Sales_Data_File_format_2001_to_Current.pdf
column_names = ["Record Type", "District Code", "Property ID", "Sale Counter", "Download Datetime", "Property Name",
             "Unit Number", "House Number", "Street Name", "Locality", "Post Code", "Area", "Area Type",
             "Contract Date", "Settlement Date", "Purchase Price", "Zoning", "Nature of Property", "Primary Purpose",
             "Strata Lot Number", "Component Code", "Sale Code", "Interest Percent", "Dealing Number", "Unknown Field"]

#-------------------------------------------------------------------------------------
# Helper function to read a single .dat file and return a Pandas dataframe
# It'll kick up a warning when it encounters bad rows, and then skip over them
# I haven't checked how many of these are in the 'B' rows that we want to keep
#-------------------------------------------------------------------------------------
def read_one_file(input_file, sep_string):
       df = pd.read_csv(input_file, sep=sep_string, names=column_names, engine='python', on_bad_lines='warn')
       # trim out all but the "B" rows
       df = df[df["Record Type"] == "B"]
       return df


#-------------------------------------------------------------------------------------
# Process all the files
# Opens the master zip, then looks in each internal zip to harvest the .dat files
# makes a list with a Pandas dataframe for each .dat
# concatenates everything into a single dataframe
#-------------------------------------------------------------------------------------
# list to hold all of the .dat contents
df_list = []

# walk through the master zip file
z_master = ZipFile(zip_of_zips_loc)
# list with each year of zipped data in the master zip
z_master_contents = z_master.namelist()

for year in z_master_contents:
       print(f"{year}")
       # crack into the zip file inside
       z_inner = ZipFile(z_master.open(year))

       # if the inner file is a zip (2015-2023)
       if z_inner.filename.lower().endswith('.zip'):
              # walk through the inner zip file and grab all the .dat
              for text_file in z_inner.infolist():
                     # print(f"\t{text_file.filename}")
                     if text_file.filename.lower().endswith('.dat'):
                            df = read_one_file(z_inner.open(text_file.filename), ";")
                            df_list.append(df)
       # otherwise, just look for the .dat directly
       elif z_inner.filename.lower().endwith('.dat'):
              if text_file.filename.lower().endswith('.dat'):
                     df = read_one_file(z_inner.open(text_file.filename), ";")
                     df_list.append(df)

# squish it all together at the end
df_all = pd.concat(df_list, axis=0, ignore_index=True)


#-------------------------------------------------------------------------------------
# If you're going to use it in Tableau, why not just write it to a .hyper file?
#-------------------------------------------------------------------------------------
from tableauhyperapi import HyperProcess, Connection, TableDefinition, SqlType, Telemetry, Inserter, CreateMode, \
       TableName, escape_string_literal

PATH_TO_HYPER = 'test_hyper_extract.hyper'

# Step 0: a little data cleaning to keep the Hyper API happy
# NaN -> None
import numpy as np
df_all_clean = df_all.replace(np.nan, None)
# make all strings (just easier for dealing with the write to .hyper)
df_all_clean = df_all_clean.applymap(str)

# Step 1: Start a new private local Hyper instance
with HyperProcess(Telemetry.SEND_USAGE_DATA_TO_TABLEAU, 'myapp') as hyper:
       print(f"Hyper connction to {PATH_TO_HYPER} is open... ready to drop in some awesome data...")
       # Step 2:  Create the the .hyper file, replace it if it already exists
       with Connection(endpoint=hyper.endpoint,
                       create_mode=CreateMode.CREATE_AND_REPLACE,
                       database=PATH_TO_HYPER) as connection:
              # Step 3: Create the schema
              connection.catalog.create_schema('Extract')
              print("Schema created...")

              # Step 4: Create the table definition
              schema = TableDefinition(table_name=TableName('Extract', 'Extract'),
                                       columns=[
                                              TableDefinition.Column("Record Type", SqlType.text()),
                                              TableDefinition.Column("District Code", SqlType.text()),
                                              TableDefinition.Column("Property ID", SqlType.text()),
                                              TableDefinition.Column("Sale Counter", SqlType.text()),
                                              TableDefinition.Column("Download Datetime", SqlType.text()),
                                              TableDefinition.Column("Property Name", SqlType.text()),
                                              TableDefinition.Column("Unit Number", SqlType.text()),
                                              TableDefinition.Column("House Number", SqlType.text()),
                                              TableDefinition.Column("Street Name", SqlType.text()),
                                              TableDefinition.Column("Locality", SqlType.text()),
                                              TableDefinition.Column("Post Code", SqlType.text()),
                                              TableDefinition.Column("Area", SqlType.text()),
                                              TableDefinition.Column("Area Type", SqlType.text()),
                                              TableDefinition.Column("Contract Date", SqlType.text()),
                                              TableDefinition.Column("Settlement Date", SqlType.text()),
                                              TableDefinition.Column("Purchase Price", SqlType.text()),
                                              TableDefinition.Column("Zoning", SqlType.text()),
                                              TableDefinition.Column("Nature of Property", SqlType.text()),
                                              TableDefinition.Column("Primary Purpose", SqlType.text()),
                                              TableDefinition.Column("Strata Lot Number", SqlType.text()),
                                              TableDefinition.Column("Component Code", SqlType.text()),
                                              TableDefinition.Column("Sale Code", SqlType.text()),
                                              TableDefinition.Column("Interest Percent", SqlType.text()),
                                              TableDefinition.Column("Dealing Number", SqlType.text()),
                                              TableDefinition.Column("Unknown Field", SqlType.text()),
                                       ])
              print("Table definition created...")

              # Step 5: Create the table in the connection catalog
              connection.catalog.create_table(schema)
              print("Table created...")

              print("Starting to insert data...")
              with Inserter(connection, schema) as inserter:
                     for index, row in df_all_clean.iterrows():
                            inserter.add_row(row)
                     inserter.execute()

              print("Boom!")
       print("The connection to the Hyper file is closed.")