# This code will process the yearly property sales data files from the NSW government website.
# The file format changed in 2001, so this assumes only data after that year.
#
# Notes on structuring your data
# There are two different formats for the downloaded data, this script will deal with both
# 2001-2014: yearly zip file with non-zipped folders inside, each containing some .dat files
#      Master Zip File
#        |__ year.ZIP
#          |__ year
#            |__ weekly folder
#              |__ .dat files
# 2015-2023: yearly zip file with zipped files inside, with each of those then containing folders with .dat
#      Master Zip File
#        |__year.ZIP
#          |__weekly.ZIP
#            |__weekly folder
#              |__ .dat files
#
# Notes:
# - This script is structured to just write a Tableau .hyper file; it does not produce a .csv
#
# Ken Flerlage has another nice variant on this problem here: https://github.com/flerlagekr/NSW-Property-Sales/blob/main/Combine.py

import pandas as pd
import numpy as np
from zipfile import ZipFile

### Big dataset from Mark T. with differing file structures (2001-2014 are same; 2015-2023 are same)
zip_of_zips_loc = r'C:\Users\sarah\Downloads\wetransfer_2002-zip_2023-02-08_2104.zip'

### Location for output .hyper file
PATH_TO_HYPER = r'C:\Users\sarah\Downloads\Mark_DAT_data.hyper'

# Column names from the Current_Property_Sales_Data_File_format_2001_to_Current.pdf
column_names = ["Record Type", "District Code", "Property ID", "Sale Counter", "Download Datetime",
                        "Property Name", "Unit Number", "House Number", "Street Name", "Locality", "Post Code", "Area",
                        "Area Type","Contract Date", "Settlement Date", "Purchase Price", "Zoning",
                        "Nature of Property", "Primary Purpose","Strata Lot Number","Component Code", "Sale Code",
                        "Interest Percent", "Dealing Number", "Unknown Field"]

#-------------------------------------------------------------------------------------
# Helper function to read a single .dat file and return a Pandas dataframe
# It currently just skips bad rows without throwing a warning, but could change to on_bad_lines='warn'
#-------------------------------------------------------------------------------------
def read_one_file(input_file, sep_string):

       df = pd.read_csv(input_file, sep=sep_string, names=column_names, engine='python', on_bad_lines='skip')
       # trim out all but the "B" rows
       df = df[df["Record Type"] == "B"]

       # NaN -> None & convert things to strings (makes it easier to write to .hyper)
       df = df.replace(np.nan, None)
       df = df.applymap(str)

       return df

#-------------------------------------------------------------------------------------
# Helper function to insert a single Pandas df to a .hyper file
#-------------------------------------------------------------------------------------
def insert_one_df(df, inserter):
       for index, row in df.iterrows():
              inserter.add_row(row)

#-------------------------------------------------------------------------------------
# Process all of the data in the master .zip file
# Write the data directly to a .hyper
#-------------------------------------------------------------------------------------
from tableauhyperapi import HyperProcess, Connection, TableDefinition, SqlType, Telemetry, Inserter, CreateMode, \
       TableName

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
              # Column names from the Current_Property_Sales_Data_File_format_2001_to_Current.pdf
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
                                              TableDefinition.Column("FileName", SqlType.text())
                                       ])
              print("Table definition created...")

              # Step 5: Create the table in the connection catalog
              connection.catalog.create_table(schema)
              print("Table created...")

              # Step 6: Insert the data
              with Inserter(connection, schema) as inserter:
                     print("Processing and inserting data...")
                     archive = ZipFile(zip_of_zips_loc, mode='r')
                     archive_contents = archive.namelist()

                     for year_zip in archive_contents:
                            # Top level folder should contain set of .zip - one for each year
                            if year_zip[-3:] == 'zip':  # marginal check; only move forward with processing .zips
                                   # open the year zip and retrieve list of files
                                   year_files = ZipFile(archive.open(year_zip))
                                   year_files_names = year_files.namelist()
                                   print(f'\t...{year_zip}')

                                   # the contents should either be a .zip or a .dat (structure changed in 2015)
                                   for year_item in year_files_names:
                                          # after 2015 - child zip inside parent zip
                                          if year_item[-3:].lower() == 'zip' and not year_item[
                                                                                     :2] == '__':  # skip internal mac files
                                                 weeks = ZipFile(year_files.open(year_item))
                                                 weeks_names = weeks.namelist()
                                                 for week in weeks_names:
                                                        if week[-3:].lower() == 'dat':
                                                               df = read_one_file(
                                                                      weeks.open(week), ";")
                                                               df['FileName'] = week
                                                               insert_one_df(df, inserter)

                                          # 2014 and earlier - .dat directly inside the parent zip
                                          elif year_item[-3:].lower() == 'dat':
                                                 df = read_one_file(
                                                        year_files.open(year_item), ";")
                                                 df['FileName'] = year_item
                                                 insert_one_df(df, inserter)
                     archive.close()
                     inserter.execute()
              print("Boom!")
       print("The connection to the Hyper file is closed.")
