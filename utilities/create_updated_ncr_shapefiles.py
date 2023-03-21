# coding: utf-8
# This script creates new versions of the GeoServer shapefiles called 
# 'all_boundaries:all_communities' and 'all_boundaries:all_areas' on
# https://gs.mapventure.org/geoserver.
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import os

# Generate point shapefile for communities
community_path = Path("../vector_data/point/alaska_point_locations.csv")
communities = pd.read_csv(community_path)
community_geometries = [Point(xy) for xy in zip(communities['longitude'], communities['latitude'])]
communities = gpd.GeoDataFrame(communities, geometry=community_geometries)
communities['type'] = 'community'
communities.set_crs(4326, inplace=True)
os.makedirs("all_places", exist_ok=True)
communities.to_file("all_places/all_communities.shp", encoding="utf-8")

# Generate concatenated multipolygon shapefile for all other areas
hucs = gpd.read_file("../vector_data/polygon/boundaries/alaska_hucs/ak_huc8s.shp")
hucs['type'] = 'huc'
huc10s = gpd.read_file("../vector_data/polygon/boundaries/alaska_hucs/ak_huc10s.shp")
huc10s['type'] = 'huc'
boroughs = gpd.read_file("../vector_data/polygon/boundaries/boroughs/ak_boroughs.shp")
boroughs['type'] = 'borough'
census = gpd.read_file("../vector_data/polygon/boundaries/census_areas/ak_census_areas.shp")
census['type'] = 'census_area'
climdiv = gpd.read_file("../vector_data/polygon/boundaries/climate_divisions/ak_climate_divisions.shp")
climdiv['type'] = 'climate_division'
corp = gpd.read_file("../vector_data/polygon/boundaries/corporation/ak_native_corporations.shp")
corp['type'] = 'corporation'
ethno = gpd.read_file("../vector_data/polygon/boundaries/ethnolinguistic/ethnolinguistic_regions.shp")
ethno['type'] = 'ethnolinguistic_region'
fire = gpd.read_file("../vector_data/polygon/boundaries/fire/ak_fire_management.shp")
fire['type'] = 'fire_zone'
first_nations = gpd.read_file("../vector_data/polygon/boundaries/first_nations/first_nation_traditional_territories.shp")
first_nations['type'] = 'first_nation'
gmu = gpd.read_file("../vector_data/polygon/boundaries/game_management_units/ak_gmu.shp")
gmu['type'] = 'game_management_unit'
ak_protected_areas = gpd.read_file("../vector_data/polygon/boundaries/protected_areas/ak_protected_areas/ak_protected_areas.shp")
ak_protected_areas['type'] = 'protected_area'
bc_protected_areas = gpd.read_file("../vector_data/polygon/boundaries/protected_areas/bc_protected_areas/bc_protected_areas.shp")
bc_protected_areas['type'] = 'protected_area'
yt_protected_areas = gpd.read_file("../vector_data/polygon/boundaries/protected_areas/yt_protected_areas/yt_protected_areas.shp")
yt_protected_areas['type'] = 'protected_area'

for gdf in [huc10s, boroughs, census, climdiv, corp, ethno, fire, first_nations,gmu,ak_protected_areas,bc_protected_areas,yt_protected_areas]:
    gdf.to_crs(4326, inplace=True)

merged = pd.concat([hucs, huc10s, boroughs, census, climdiv, corp, ethno, fire, first_nations, gmu, ak_protected_areas, bc_protected_areas, yt_protected_areas])
merged = merged.drop(columns=['region','country','states','FIPS','agency','subunit','sublabel'])

merged.to_file("all_places/all_areas.shp", encoding="utf-8")

akhuc12 = gpd.read_file("../vector_data/polygon/boundaries/alaska_hucs/ak_huc12s.shp")
akhuc12['type'] = 'huc12'
akhuc12.to_crs(4326, inplace=True)
akhuc12.to_file("all_places/ak_huc12s.shp", encoding="utf-8")