"""
This utility is used to add tags to the "tags" column of point location CSV
files. It will overwrite any existing tag in the tags column currently, but we
can modify this script to be more sophisticated as needed. The script outputs
the tagged CSVs to a new directory called "tagged_csvs", from where they can be
copied into the vector_data/point directory.
"""

import os
import csv
import glob
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, box

# ardac = ARDAC Explorer
# awe = Alaska Wildfire Explorer
# eds = Arctic-EDS
# ncr = Northern Climate Reports

file_tags = {
    "alaska_point_locations.csv": ["eds", "ardac", "awe"],
}

tags_for_all_locations = ["ardac"]

check_within_iem = [
    "alaska_point_locations.csv",
    "british_columbia_point_locations.csv",
    "yukon_point_locations.csv",
]

check_within_aqi_geotiff = [
    "british_columbia_point_locations.csv",
    "yukon_point_locations.csv",
]

# Military sites to include in Arctic-EDS but no other webapps
eds_only = [
    "AK557",
    "AK558",
    "AK559",
    "AK560",
    "AK561",
    "AK562",
    "AK563",
    "AK564",
    "AK565",
    "AK566",
    "AK567",
    "AK568",
    "AK569",
    "AK570",
    "AK571",
    "AK572",
    "AK573",
    "AK574",
    "AK575",
    "AK576",
    "AK577",
    "AK578",
    "AK579",
    "AK580",
    "AK581",
    "AK582",
    "AK583",
    "AK584",
    "AK585",
]

if not os.path.exists("tagged_csvs"):
    os.makedirs("tagged_csvs")

# Load the IEM AOI mask
iem_gdf = gpd.read_file(
    "../vector_data/polygon/boundaries/iem_with_ak_aleutians/iem_with_ak_aleutians.shp"
)
iem_gdf.to_crs(4326, inplace=True)

# BBOX coordinates taken from an example aqi_forecast_24_hrs.tif file
aqi_bbox = box(-1783505.405, 484131.432, 1134455.303, 2733401.487)
aqi_gdf = gpd.GeoDataFrame({"geometry": [aqi_bbox]}, crs="EPSG:3338")


def add_tags_within_polygon(communities, polygon_gdf, tag):
    """Tag communities with provided tag if they are within the polygon_gdf"""
    # Ensure communities are in the same CRS as polygon_gdf

    # Find communities within the polygon_gdf
    polygon_communities = communities.to_crs(polygon_gdf.crs).within(
        polygon_gdf.geometry.unary_union
    )

    # Filter out communities that are in eds_only
    polygon_communities = polygon_communities & ~communities["id"].isin(eds_only)

    # Tag remaining communities with provided tag
    tags = communities.loc[polygon_communities, "tags"].str.split(",")
    tags = tags.apply(lambda x: x + [tag])
    tags = tags.apply(sorted)
    communities.loc[polygon_communities, "tags"] = tags.apply(lambda x: ",".join(x))

    return communities


for path in glob.iglob("../vector_data/point/*.csv"):
    file = os.path.basename(path)
    communities = pd.read_csv(path)
    columns = communities.columns

    if "tags" not in communities.columns:
        communities["tags"] = ""
        columns = list(columns) + ["tags"]

    # Add "eds" to all communities with ID in eds_only
    communities["tags"] = communities["tags"].astype(str)
    communities.loc[communities["id"].isin(eds_only), "tags"] = "eds"

    # Add tags to communities that are not in eds_only
    tags = tags_for_all_locations.copy()

    if file in file_tags:
        tags += file_tags[file]
    communities.loc[~communities["id"].isin(eds_only), "tags"] = ",".join(tags)

    if file in check_within_iem:
        geometries = [
            Point(xy) for xy in zip(communities["longitude"], communities["latitude"])
        ]
        communities = gpd.GeoDataFrame(
            communities, geometry=geometries, crs="EPSG:4326"
        )

        communities = add_tags_within_polygon(communities, iem_gdf, "ncr")
        communities = add_tags_within_polygon(communities, aqi_gdf, "awe")

        # Remove the geometry column before writing to CSV
        communities = communities.drop(columns="geometry")

    # Sort tags and remove duplicates if they exist
    communities["tags"] = communities["tags"].str.split(",")
    communities["tags"] = communities["tags"].apply(set).apply(list).apply(sorted)
    communities["tags"] = communities["tags"].apply(lambda x: ",".join(x))

    # Replace all nans with empty strings
    communities = communities.fillna("")

    # Convert back to a list of dicts
    new_csv = communities.to_dict("records")

    with open(f"tagged_csvs/{file}", "w") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(new_csv)
