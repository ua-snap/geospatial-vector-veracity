"""This script was used to simplify the HUC-12 shapefile
and reproject it to EPSG:3338.
Assumes original WGS84 HUC-12 shapefile is present in working directory.
"""

import geopandas as gpd


# default name of file
huc12_gdf = gpd.read_file("wbdhu12_a_ak.shp").to_crs(3338)
new_huc_geoms = huc12_gdf["geometry"].simplify(100, preserve_topology=True)
new_gdf = huc12_gdf.copy()
new_gdf["geometry"] = new_huc_geoms
new_gdf = new_gdf.rename(columns={"huc12": "id"})
new_gdf = new_gdf[["id", "name", "states", "geometry"]]
# drop cook inlet, kotzebue sound, Aleutians HUC, St Lawrence Island
drop_hucs = ["190208000003", "190505000000", "190301030000", "190501010000"]
new_gdf = new_gdf[~new_gdf["id"].isin(drop_hucs)]
new_gdf.to_file("ak_huc12s.shp")
