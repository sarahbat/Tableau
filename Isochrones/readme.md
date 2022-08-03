A quick script to input a point file (currently just using a shapefile, but easily modifiable to read in a .csv or other input), call out to the [Mapbox Isochrone API](https://docs.mapbox.com/playground/isochrone/) and write a .hyper file with the geometry returned

Interesting input options:
* Profiles for the isochrones (walking, driving, cycling are all options)
* Varying distances for the isochrones (add other distances to the array as desired)


I'm not responsible for any usage fees that you accrue from Mapbox running the API.  Look at Mapbox's [documentation](https://docs.mapbox.com/api/navigation/isochrone/) and [pricing](https://docs.mapbox.com/api/navigation/isochrone/#isochrone-api-pricing) as needed 
