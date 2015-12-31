Data source: https://data.cityofchicago.org/Transportation/Metra-Stations/nqm8-q2ym

I set up the QGIS file based on the CRS listed in the .prj file.

Update Procedure method 1: command line using OGR tools

    rm metraapi/MetraStations.csv
    ogr2ogr -f CSV metraapi/MetraStations.csv gis/MetraStations.shp -lco GEOMETRY=AS_WKT

Update Procedure method 2: GUI

 1) Update GIS files
 2) Open in QGIS
 3) Right click MetraStations layer
 4) Save as
 5) Select Layer Options -> GEOMETRY -> AS_WKT
 6) Export to metraapi/MetraStations.csv over existing file
