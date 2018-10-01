# @sarahbat (Sarah Battersby)
#
# Read address data from csv, write geocoded results to csv
# Adjust address based on the relevant comments in your input csv
#
# Python = 2.7

import csv
import censusgeocode as cg

file_input = 'c:/temp/test.csv'
file_output = 'c:/temp/test_output.csv'

with open(file_input) as csv_input:
  with open(file_output, 'w') as csv_output:
    csv_reader = csv.reader(csv_input, delimiter=',')
    csv_writer = csv.writer(csv_output, delimiter='|', lineterminator='\n')
    csv_writer.writerow(['address'] + ['longitude'] + ['latitude'] + ['id'])

    line_count = 0
    for row in csv_reader:
      if line_count == 0:
        line_count += 1
        continue
      else:
        # make address from relevant columns in csv (will vary depending on input format)
        address = row[7] + ', ' + row[8] + ', ' + row[9] + ' ' + row[12]
        # geocode using Census; if match, write to csv
        try:
          address_geocode = cg.onelineaddress(address)
          if len(address) > 0: # there is a match
            csv_writer.writerow([address] + [address_geocode[0]['coordinates']['x']] +
              [address_geocode[0]['coordinates']['y']] + [line_count])
          else:
            # address not matched
            addwriter.writerow([address] + ['-99'] + ['-99'] + [line_count])
        except:
          print 'geocode failed for ' + address
          # address not matched
          addwriter.writerow([address] + ['-99'] + ['-99'] + [line_count])
        line_count += 1
