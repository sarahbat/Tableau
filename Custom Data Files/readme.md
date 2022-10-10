### Datasets with "modified geographies" to use in Tableau

This is a storage spot for the custom geographic data that I have made for use in Tableau.

#### US Census
Standard US Census cartographic boundary files (just the 50 states), modified to shift Alaska and Hawaii closer to the Lower 48, and to trick Tableau into displaying in Albers Equal Area projection.

Note that you cannot use the standard Tableau map tiles, geocoding roles, or geographic search with these files as they do require a bit of creative lying about the map projection.

* States (1:20m)
* Counties (1:20m)
* Census tracts (1:500k - but simplified using Mapshaper)
* Block groups (1:500k - but simplified using Mapshaper)
