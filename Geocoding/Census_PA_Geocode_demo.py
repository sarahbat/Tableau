# @sarahbat (Sarah Battersby)
#
# Read address data from csv, write geocoded results to csv
# Demo using kinda random Philadelphia addresses (from city Open data portal - real estate tax delinquincy data)
# Census geocoder
# FWIW - census geocoder on ~10000 records ran for ~7hrs 13min
# No match on 248 entries

import csv
import censusgeocode as cg

file_input = r'philly_real_estate_tax_delinquencies_geocode_10k.csv'
file_output = r'output\philly_real_estate_tax_delinquencies_geocode_10k_output.csv'
ID_FIELD = 0
ADDRESS_FIELD = 1
CITY_FIELD = 2
STATE_FIELD = 3
ZIP_FIELD = 4

with open(file_input) as csv_input:
  with open(file_output, 'w') as csv_output:
    csv_reader = csv.reader(csv_input, delimiter=',')
    csv_writer = csv.writer(csv_output, delimiter='|', lineterminator='\n')
    csv_writer.writerow(['address'] + ['longitude'] + ['latitude'] + ['rowNum'] + ['id'])

    line_count = 0
    for row in csv_reader:
      if line_count == 0:
        line_count += 1
        continue
#       if line_count == 10:
#         break
      else:
        # make address from relevant columns in csv (will vary depending on input format)
        address = row[ADDRESS_FIELD] + ', ' + row[CITY_FIELD] + ', ' + row[STATE_FIELD] + ' ' + row[ZIP_FIELD]
        id_val = row[ID_FIELD]
        # geocode using Census; if match, write to csv
        try:
          address_geocode = cg.onelineaddress(address)
          if len(address) > 0: # there is a match
            csv_writer.writerow([address] + [address_geocode[0]['coordinates']['x']] +
              [address_geocode[0]['coordinates']['y']] + [line_count] + [row[ID_FIELD]])
          else:
            # address not matched
            csv_writer.writerow([address] + ['-99'] + ['-99'] + [line_count] + [row[ID_FIELD]])
        except:
          print('geocode failed for ' + address)
          # address not matched
          csv_writer.writerow([address] + ['-99'] + ['-99'] + [line_count] + [row[ID_FIELD]])
        line_count += 1
