GIS Data
========

The GIS sourcing supplies the latitude, longitude, address, municipality, bike parking, fare zone, station id, branch id (although these IDs may be of limited usefulness) information for MetraAPI.

Data source: https://data.cityofchicago.org/Transportation/Metra-Stations/nqm8-q2ym

I set up the QGIS file based on the CRS listed in the .prj file.

Update Procedure method 1: command line using OGR tools
-------------------------------------------------------

    rm metraapi/MetraStations.csv
    ogr2ogr -f CSV metraapi/MetraStations.csv gis/MetraStations.shp -lco GEOMETRY=AS_WKT

Update Procedure method 2: GUI
------------------------------

* Update GIS files
* Open `MetraStations.qgs` in QGIS
* Right click MetraStations layer
* Save as
* Select Layer Options -> GEOMETRY -> AS_WKT
* Export to `metraapi/MetraStations.csv` over existing file
