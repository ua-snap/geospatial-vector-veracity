# coding: utf-8
# This script creates new versions of the GeoServer shapefiles called
# 'all_boundaries:all_communities' and 'all_boundaries:all_areas' on
# https://gs.mapventure.org/geoserver.
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import os

# Load the IEM AOI mask
mask_gdf = gpd.read_file(
    "../vector_data/polygon/boundaries/iem_with_ak_aleutians/iem_with_ak_aleutians.shp"
)
mask_gdf.to_crs(4326, inplace=True)

# Load community point geometries and set CRS
community_path = Path("../vector_data/point/")
community_csvs = [
    "alaska_point_locations.csv",
    "yukon_point_locations.csv",
    "british_columbia_point_locations.csv",
]
communities = pd.concat(
    [pd.read_csv(f"{community_path}/{csv}") for csv in community_csvs]
)
community_geometries = [
    Point(xy) for xy in zip(communities["longitude"], communities["latitude"])
]
communities = gpd.GeoDataFrame(communities, geometry=community_geometries)
communities["type"] = "community"

# Remove Attu as it wraps over dateline and has no relevant data
attu = communities.loc[communities["name"] == "Attu"]
communities = communities.drop(attu.index)

# Renames column because ESRI Shapefiles have a hard limit of 10 characters
# for column names.
communities = communities.rename(columns={"km_distance_to_ocean": "km2ocean"})
communities.set_crs(4326, inplace=True)

# Find all communities within the IEM AOI
communities = communities[communities.within(mask_gdf.geometry.unary_union)]

schema = {
    "geometry": "Point",
    "properties": {
        "id": "str",
        "name": "str",
        "alt_name": "str",
        "region": "str",
        "country": "str",
        "latitude": "float",
        "longitude": "float",
        "km2ocean": "float",
        "type": "str",
    },
    "Y_PRECISION": 4,
    "X_PRECISION": 4,
}

# Write result to shapefile
os.makedirs("all_places", exist_ok=True)
communities.to_file(
    "all_places/all_communities.shp",
    engine="fiona",
    driver="ESRI Shapefile",
    encoding="utf-8",
    schema=schema,
)

# Generate concatenated multipolygon shapefile for all other areas
hucs = gpd.read_file("../vector_data/polygon/boundaries/alaska_hucs/ak_huc8s.shp")
hucs["type"] = "huc"
hucs["area_type"] = "HUC8"

huc10s = gpd.read_file("../vector_data/polygon/boundaries/alaska_hucs/ak_huc10s.shp")
huc10s["type"] = "huc"
huc10s["area_type"] = "HUC10"

boroughs = gpd.read_file("../vector_data/polygon/boundaries/boroughs/ak_boroughs.shp")
boroughs["type"] = "borough"

census = gpd.read_file(
    "../vector_data/polygon/boundaries/census_areas/ak_census_areas.shp"
)
census["type"] = "census_area"

climdiv = gpd.read_file(
    "../vector_data/polygon/boundaries/climate_divisions/ak_climate_divisions.shp"
)
climdiv["type"] = "climate_division"

corp = gpd.read_file(
    "../vector_data/polygon/boundaries/corporation/ak_native_corporations.shp"
)
corp["type"] = "corporation"

ethno = gpd.read_file(
    "../vector_data/polygon/boundaries/ethnolinguistic/ethnolinguistic_regions.shp"
)
ethno["type"] = "ethnolinguistic_region"

fire = gpd.read_file("../vector_data/polygon/boundaries/fire/ak_fire_management.shp")
fire["type"] = "fire_zone"

first_nations = gpd.read_file(
    "../vector_data/polygon/boundaries/first_nations/first_nation_traditional_territories.shp"
)
first_nations["type"] = "first_nation"

gmu = gpd.read_file(
    "../vector_data/polygon/boundaries/game_management_units/ak_gmu.shp"
)
gmu["type"] = "game_management_unit"

ak_protected_areas = gpd.read_file(
    "../vector_data/polygon/boundaries/protected_areas/ak_protected_areas/ak_protected_areas.shp"
)
ak_protected_areas["type"] = "protected_area"
bc_protected_areas = gpd.read_file(
    "../vector_data/polygon/boundaries/protected_areas/bc_protected_areas/bc_protected_areas.shp"
)
bc_protected_areas["type"] = "protected_area"
yt_protected_areas = gpd.read_file(
    "../vector_data/polygon/boundaries/protected_areas/yt_protected_areas/yt_protected_areas.shp"
)
yt_protected_areas["type"] = "protected_area"

for gdf in [
    huc10s,
    boroughs,
    census,
    climdiv,
    corp,
    ethno,
    fire,
    first_nations,
    gmu,
    ak_protected_areas,
    bc_protected_areas,
    yt_protected_areas,
]:
    # Clips all geometries to the western hemisphere
    gdf["geometry"] = gpd.clip(gdf["geometry"], [-180, -90, 0, 90])
    gdf.to_crs(4326, inplace=True)

# Only keep British Columbia & Yukon Territory protected areas
# within the IEM AOI.
bc_protected_areas = bc_protected_areas[
    bc_protected_areas.within(mask_gdf.geometry.unary_union)
]
yt_protected_areas = yt_protected_areas[
    yt_protected_areas.within(mask_gdf.geometry.unary_union)
]

# Merge all of the areas into a single Pandas data frame
merged = pd.concat(
    [
        hucs,
        huc10s,
        boroughs,
        census,
        climdiv,
        corp,
        ethno,
        fire,
        first_nations,
        gmu,
        ak_protected_areas,
        bc_protected_areas,
        yt_protected_areas,
    ]
)

# Drops all unused metadata from the areas
merged = merged.drop(
    columns=["region", "country", "states", "FIPS", "agency", "subunit", "sublabel"]
)

merged.to_file("all_places/all_areas.shp", encoding="utf-8")

# Generate HUC12 shapefile with type added
akhuc12 = gpd.read_file("../vector_data/polygon/boundaries/alaska_hucs/ak_huc12s.shp")
akhuc12["type"] = "huc12"
akhuc12.to_crs(4326, inplace=True)

akhuc12.to_file("all_places/ak_huc12s.shp", encoding="utf-8")
