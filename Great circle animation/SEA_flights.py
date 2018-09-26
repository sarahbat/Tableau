


from tableausdk import Type
from tableausdk.Extract import *
from geographiclib.geodesic import Geodesic
import csv


# Where the origin data comes from
csvLocation = 'data/SEA_flights_09152017.csv'

# Where the TDE will be written
extractLocation = 'sea_flight_points_1min.tde'

# csv column number for origin/destination coordinates (start count at 0 for the first col in your csv)
ORIG_LAT = 7
ORIG_LON  = 8
DEST_LAT =  3
DEST_LON =  4
SEG_NAME = 9
DEP_TIME = 6 # Departure time (minutes from midnight)
DEP_TIME_HRS = 0
FLIGHT_NUM = 2
FLIGHT_TIME = 5

#####################################################################
## Process the data and write the TDE
#####################################################################

# 1. initialize a new extract
ExtractAPI.initialize()

# 2. Create a table definition
new_extract = Extract(extractLocation)

# 3. Add column definitions to the table definition
table_definition = TableDefinition()
table_definition.addColumn('route', Type.UNICODE_STRING)  # column 0
table_definition.addColumn('latitude', Type.DOUBLE)
table_definition.addColumn('longitude', Type.DOUBLE)
table_definition.addColumn('point_number', Type.INTEGER)
table_definition.addColumn('distance_km', Type.DOUBLE)
table_definition.addColumn('FlightNumber', Type.UNICODE_STRING)
table_definition.addColumn('DepartureTime', Type.UNICODE_STRING)
table_definition.addColumn('DepartureTimeFromMidnight', Type.UNICODE_STRING)
table_definition.addColumn('SegMinFromMidnight', Type.INTEGER)
table_definition.addColumn('FlightTime', Type.INTEGER)
table_definition.addColumn('SegTimeFromMidnight', Type.UNICODE_STRING)

# 4. Initialize a new table in the extract
if (new_extract.hasTable('Extract') == False):
  new_table = new_extract.addTable('Extract', table_definition)
else:
  new_table = new_extract.openTable('Extract')

# 5. Create a new row
new_row = Row(table_definition)  # Pass the table definition to the constructor

# 6. walk through the origin/destination data from CSV, write each path to TDE
with open(csvLocation, 'rb') as csvfile:
  csvreader = csv.reader(csvfile, delimiter='|')

  next(csvreader) # skip header


  for row in csvreader:
    # print row
    olat = float(row[ORIG_LAT])
    olon = float(row[ORIG_LON])
    dlat = float(row[DEST_LAT])
    dlon = float(row[DEST_LON])
    route = row[SEG_NAME]
    depTime_midnight = row[DEP_TIME]
    depTime_hrs = row[DEP_TIME_HRS]
    flightTime = int(row[FLIGHT_TIME])
    flightNum = row[FLIGHT_NUM]

  # Calculate geodesic
    p = Geodesic.WGS84.Inverse(olat, olon, dlat, dlon)
    l = Geodesic.WGS84.Line(p['lat1'], p['lon1'], p['azi1'])
    SEG_TIME = 1 # 1 minute chunks for the points on the path
    num = int(round(flightTime) / SEG_TIME) # how many points needed for the path

    # for every point on the path - get the position at designated time, set the time stamp
    for i in range(num + 1)
      b = l.Position(i * p['s12'] / num, Geodesic.STANDARD | Geodesic.LONG_UNROLL)
      minFromMidnight = int(depTime_midnight) + (i * SEG_TIME)
      hrFromMidnight = minFromMidnight / 60
      hrFromMidight_str = ''
      if (hrFromMidnight > 24):
        hrFromMidight_str = "+1 day "
        hrFromMidnight = hrFromMidnight - 24
      hrFromMidight_str += str(hrFromMidnight)

      # bin to 15 min chunks
      timeFromMidnight = hrFromMidight_str + ":" + str(((minFromMidnight%60)/15) * 15)
      # write a row in the TDE for each point on the path
      new_row.setString(0, route)
      new_row.setDouble(1, b['lat2'])
      new_row.setDouble(2, b['lon2'])
      new_row.setInteger(3, i)
      new_row.setDouble(4, p['s12'] / 1000)
      new_row.setString(5, flightNum)
      new_row.setString(6, depTime_hrs)
      new_row.setString(7, depTime_midnight)
      new_row.setInteger(8, minFromMidnight ) # time (from midnight, in min) at this point
      new_row.setInteger(9, flightTime)
      new_row.setString(10, timeFromMidnight) # segment time in hours from midnight
      new_table.insert(new_row)

# 7. Save the table and extract
new_extract.close()

# 8. Release the extract API
ExtractAPI.cleanup()

print 'Finished!  Enjoy your TDE'
