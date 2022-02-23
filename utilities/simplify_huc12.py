"""This script was used to simplify the HUC-12 shapefile
and reproject it to EPSG:3338.
Assumes original WGS84 HUC-12 shapefile is present in working directory.
"""

import geopandas as gpd


huc12_gdf = gpd.read_file("hydrologic_units_wbdhu12_a_ak.shp").to_crs("EPSG:3338")
new_huc_geoms = huc12_gdf["geometry"].simplify(100, preserve_topology=True)
new_gdf = huc12_gdf.copy()
new_gdf["geometry"] = new_huc_geoms
new_gdf.to_file("hydrologic_units_wbdhu12_a_ak_simplified.shp")
