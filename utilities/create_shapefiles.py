# coding: utf-8
# This script creates new versions of the GeoServer shapefiles called
# 'all_boundaries:all_communities' and 'all_boundaries:all_areas' on
# https://gs.mapventure.org/geoserver.
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import glob
import os

# Load the IEM AOI mask
mask_gdf = gpd.read_file(
    "../vector_data/polygon/boundaries/iem_with_ak_aleutians/iem_with_ak_aleutians.shp"
)
mask_gdf.to_crs(4326, inplace=True)

# Load community point geometries and set CRS
communities = pd.concat(
    [pd.read_csv(csv) for csv in glob.iglob("../vector_data/point/*.csv")]
)
community_geometries = [
    Point(xy) for xy in zip(communities["longitude"], communities["latitude"])
]
communities = gpd.GeoDataFrame(communities, geometry=community_geometries)
communities["type"] = "community"

# Reindex combined CSV dataframe so each row has a unique index. This is
# necessary so that dropping a row doesn't accidentally drop other rows.
communities = communities.reset_index(drop=True)

# Remove Attu as it wraps over dateline and has no relevant data
attu = communities.loc[communities["name"] == "Attu"]
communities = communities.drop(attu.index)

# Renames column because ESRI Shapefiles have a hard limit of 10 characters
# for column names.
communities = communities.rename(columns={"km_distance_to_ocean": "km2ocean"})
communities.set_crs(4326, inplace=True)

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
        "tags": "str",
        "is_coastal": "bool",
        "ocean_lat1": "float",
        "ocean_lon1": "float",
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
huc8s = gpd.read_file("../vector_data/polygon/boundaries/alaska_hucs/ak_huc8s.shp")
huc8s["type"] = "huc"
huc8s["area_type"] = "HUC8"

huc10s = gpd.read_file("../vector_data/polygon/boundaries/alaska_hucs/ak_huc10s.shp")
huc10s["type"] = "huc"
huc10s["area_type"] = "HUC10"

huc12s = gpd.read_file("../vector_data/polygon/boundaries/alaska_hucs/ak_huc12s.shp")
huc12s["type"] = "huc"
huc12s["area_type"] = "HUC12"

yt_watersheds = gpd.read_file(
    "../vector_data/polygon/boundaries/yt_watersheds/yt_watersheds4326.shp"
)
yt_watersheds["type"] = "yt_watershed"
yt_watersheds["area_type"] = "Yukon Watershed"

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

ak_fire = gpd.read_file(
    "../vector_data/polygon/boundaries/fire/ak_fire_mgmt/ak_fire_management.shp"
)
ak_fire["type"] = "fire_zone"

yt_fire = gpd.read_file(
    "../vector_data/polygon/boundaries/fire/yt_fire_mgmt/yt_fire_management_4326.shp"
)
yt_fire["type"] = "yt_fire_district"
yt_fire["area_type"] = "Yukon Fire District"

first_nations = gpd.read_file(
    "../vector_data/polygon/boundaries/first_nations/first_nation_traditional_territories.shp"
)
first_nations["type"] = "first_nation"

ak_gmu = gpd.read_file(
    "../vector_data/polygon/boundaries/game_management_units/ak_gmus/ak_gmu.shp"
)
ak_gmu["type"] = "game_management_unit"

yt_gmsz = gpd.read_file(
    "../vector_data/polygon/boundaries/game_management_units/yt_gmzs/yt_game_management_zones4326.shp"
)
yt_gmsz["type"] = "yt_game_management_subzone"
yt_gmsz["area_type"] = "Yukon Game Management Subzone"

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
    huc8s,
    huc10s,
    huc12s,
    yt_watersheds,
    boroughs,
    census,
    climdiv,
    corp,
    ethno,
    ak_fire,
    yt_fire,
    first_nations,
    ak_gmu,
    yt_gmsz,
    ak_protected_areas,
    bc_protected_areas,
    yt_protected_areas,
]:
    if gdf.crs != "EPSG:4326":
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
        huc8s,
        huc10s,
        huc12s,
        yt_watersheds,
        boroughs,
        census,
        climdiv,
        corp,
        ethno,
        ak_fire,
        yt_fire,
        first_nations,
        ak_gmu,
        yt_gmsz,
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
