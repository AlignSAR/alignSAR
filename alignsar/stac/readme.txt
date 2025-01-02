Conversion of data into a cloud-native data format
The resultant NetCDF files can be converted into a cloud-native data format so that they can be made available through a STAC (SpatioTemporal Asset Catalogs) catalog in an efficient manner. Furthermore, they need to be georeferenced so that they can be searched and accessed by using spatiotemporal queries supported by the STAC specification.

To create such cloud-optimized geospatial data files of the assets, the layers stored as variables in the NetCDF files were first extracted as individual GeoTIFF files [1]. For this purpose, gdal_translate utility from the GDAL Library of the Open Source Geospatial Foundation was utilized that converts raster data between different formats [2].

32-bit floating point data type was used for all files and convert.py script was used to generate the necessary commands to create GeoTIFF files, which followed the following pattern: 
gdal_translate -ot Float32 "NETCDF:<input.nc>:<variable_name>" <output.tif>

The data in NetCDF files are in gridded radar coordinates; hence, do not have embedded geographic coordinates. But latitude and longitude information are provided as separate variables for each grid cell. This information was used for georeferencing of generated GeoTIFF raster files.

For this purpose, first a number of ground control points (GCPs) were generated from the latitude and longitude grids. Then, these GCPs were added to the GeoTIFF raster files. Finally, the raster files were reprojected by using these GPCs to a geographic coordinate reference system (CRS), which represents Earth’s surface as a three-dimensional ellipsoid. EPSG:4326 projection based on WGS84 ellipsoid was used as the CRS of all data files.

To obtain the GPCs, 100 regularly distributed latitude and longitude pairs on a 10 x 10 grid covering the whole raster grid were extracted from each NetCDF file. Attention was paid to include all 4 corner points (i.e., northwest, northeast, southeast, and southwest corners) for a complete reprojection. 

gcps.py script was used to extract the coordinates. Extracted GCPs were stored as a separate CSV file for each NetCDF file. Each CSV file contains 4 columns, which are x, y, longitude, and latitude values. x and y columns correspond to the centre location of a cell in zero-based grid coordinates, e.g. 0.5 and 0.5 for the top left cell, and longitude and latitude correspond to matching geographic coordinates. 
To enable visual inspection of the GCPs with QGIS, they were also provided as Points files which are also CSV files but with a different structure. Each Points file has 5 columns, which are longitude, latitude, x, -y, and enabled. Enabled column is always 1, as all GCPs were used for reprojection purposes. points.py script was used to convert the original CSV files to Points files.

gdal_translate utility was used to add the generated GCPs to the related GeoTIFF files, and gdalwrap utility was used to reproject them. During the reprojection, nearest neighbour resampling method was used to preserve the original cell values. The output format of reprojection was also set as Cloud Optimized GeoTIFF (COG) [3], as the resulting raster files were used for the STAC catalog. 

georeference.py script was used to generate the necessary commands to create georeferenced COG files, which followed the following pattern for each file:
gdal_translate -strict -of GTiff -a_srs EPSG:4326 -stats <GCPs> <input.tif> <temp.tif>
gdalwrap -r near -of COG -t_srs EPSG:4326 <temp.tif> <output.tif> 
By running the generated commands, all AlignSAR data files were converted to cloud-native COG format suitable for creating the STAC catalog.


References
[1] Devys, E., Habermann, T., Heazel, C., Lott, R., & Rouault, E. (eds.) (2019). OGC GeoTIFF Standard. https://docs.ogc.org/is/19-008r4/19-008r4.html 
[2] Rouault, E., Warmerdam, F., Schwehr, K., Kiselev, A., Butler, H., Łoskot, M., Szekeres, T., Tourigny, E., Landa, M., Miara, I., Elliston, B., Chaitanya, K., Plesea, L., Morissette, D., Jolma, A., Dawson, N., Baston, D., de Stigter, C., & Miura, H. (2024). GDAL (v3.8.3). Zenodo. https://doi.org/10.5281/zenodo.10472126 
[3] Maso, J. (ed.) (2023). OGC Cloud Optimized GeoTIFF Standard. https://docs.ogc.org/is/21-026/21-026.html 
[4] COG – Cloud Optimized GeoTIFF Generator in GDAL Documentation. (2023). https://gdal.org/drivers/raster/cog.html 


