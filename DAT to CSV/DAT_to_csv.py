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
from zipfile import ZipFile

### Big dataset from Mark T. with differing file structures (2001-2014 are same; 2015-2023 are same)
zip_of_zips_loc = r'C:\Users\sarah\Downloads\wetransfer_2002-zip_2023-02-08_2104.zip'

### Location for output .csv file
PATH_TO_CSV = r'C:\Users\sarah\Downloads\Mark_DAT_data.csv'

column_names = ["Record Type", "District Code", "Property ID", "Sale Counter", "Download Datetime",
                        "Property Name", "Unit Number", "House Number", "Street Name", "Locality", "Post Code", "Area",
                        "Area Type","Contract Date", "Settlement Date", "Purchase Price", "Zoning",
                        "Nature of Property", "Primary Purpose","Strata Lot Number","Component Code", "Sale Code",
                        "Interest Percent", "Dealing Number", "Unknown Field", "FileName"]

#-------------------------------------------------------------------------------------
# Helper function to read a single .dat file and return a Pandas dataframe
# It currently just skips bad rows without throwing a warning, but could change to on_bad_lines='warn'
#-------------------------------------------------------------------------------------
def read_one_file(input_file, sep_string):
        df = pd.read_csv(input_file, sep=sep_string, names=column_names, engine='python', on_bad_lines='skip')
        # trim out all but the "B" rows
        df = df[df["Record Type"] == "B"]

        return df

#-------------------------------------------------------------------------------------
# Process all of the data in the master .zip file
# Write the data to a .csv
#-------------------------------------------------------------------------------------

archive = ZipFile(zip_of_zips_loc, mode='r')
archive_contents = archive.namelist()

df = pd.DataFrame(columns=column_names)
df.to_csv(PATH_TO_CSV)

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
                                       df.to_csv(PATH_TO_CSV, mode='a', index=True, header=False)

                  # 2014 and earlier - .dat directly inside the parent zip
                  elif year_item[-3:].lower() == 'dat':
                         df = read_one_file(
                                year_files.open(year_item), ";")
                         df['FileName'] = year_item
                         df.to_csv(PATH_TO_CSV, mode='a', index=True, header=False)
