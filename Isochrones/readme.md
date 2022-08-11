A quick set of scripts to input point data (single hard-coded point, a csv with lat/lng, or a point shapefile), call out to the [Mapbox Isochrone API](https://docs.mapbox.com/playground/isochrone/) and write a .hyper file with the geometry returned

Interesting input options:
* Profiles for the isochrones (walking, driving, cycling are all options)
* Varying distances for the isochrones (add other distances to the array, or set a range of min/max time distances for a single point)

Files to choose from:
* *Mapbox_isochrones_shp_to_hyper.py* - Input a point SHAPEFILE and generate isochrones around every row of points in the file. Writes a new COLUMN for each profile/distance combination.
* *Mapbox_isochrones_csv_to_hyper.py* - Input a CSV with latitude and longitude columns and generate generate isochrones around every row of lat/lng defined points in the file. Writes a new COLUMN for each profile/distance combination.
* *Mapbox_isochrones_range_one_point.py* - Input a SINGLE point location as hard coded lat/lng and generate a range of isochrones based on min distance, max distance, and a step size (e.g., if you want to generate walking isochrones at 1 minute interval around a location, from 1-60 minutes). Writes a new ROW for each profile/distance combination.

I'm not responsible for any usage fees that you accrue from Mapbox running the API.  Look at Mapbox's [documentation](https://docs.mapbox.com/api/navigation/isochrone/) and [pricing](https://docs.mapbox.com/api/navigation/isochrone/#isochrone-api-pricing) as needed 
