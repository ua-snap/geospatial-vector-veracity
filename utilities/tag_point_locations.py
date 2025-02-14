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
from shapely.geometry import Point

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
    tags = list(set(tags))
    tags = sorted(tags)
    communities.loc[~communities["id"].isin(eds_only), "tags"] = ",".join(tags)

    if file in check_within_iem:
        geometries = [
            Point(xy) for xy in zip(communities["longitude"], communities["latitude"])
        ]
        communities = gpd.GeoDataFrame(communities, geometry=geometries)

        # Find communities within the IEM polygon
        iem_communities = communities.within(iem_gdf.geometry.unary_union)

        # Filter out communities that are in eds_only
        iem_communities = iem_communities & ~communities["id"].isin(eds_only)

        # Tag remaining communities with "ncr"
        tags = communities.loc[iem_communities, "tags"].str.split(",")
        tags = tags.apply(lambda x: x + ["ncr"])
        tags = tags.apply(sorted)
        communities.loc[iem_communities, "tags"] = tags.apply(lambda x: ",".join(x))

        # Remove the geometry column before writing to CSV
        communities = communities.drop(columns="geometry")

    # Replace all nans with empty strings
    communities = communities.fillna("")

    # Convert back to a list of dicts
    new_csv = communities.to_dict("records")

    with open(f"tagged_csvs/{file}", "w") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(new_csv)
