"""
This utility is used to add tags to the "tags" column of point location CSV
files. It will overwrite any existing tag in the tags column currently, but we
can modify this script to be more sophisticated as needed. The scirpt outputs
the tagged CSVs to a new directory called "tagged_csvs", from where they can be
copied into the vector_data/point directory.
"""

import os
import csv
import glob
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

file_tags = {
    "alaska_point_locations.csv": ["eds", "ardac"],
    "alberta_point_locations.csv": ["ardac"],
    "british_columbia_point_locations.csv": ["ardac"],
    "manitoba_point_locations.csv": ["ardac"],
    "northwest_territories_point_locations.csv": ["ardac"],
    "saskatchewan_point_locations.csv": ["ardac"],
    "yukon_point_locations.csv": ["ardac"],
}

check_within_iem = [
    "alaska_point_locations.csv",
    "british_columbia_point_locations.csv",
    "yukon_point_locations.csv",
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

    tags = file_tags[file]
    communities["tags"] = ",".join(tags)

    if file in check_within_iem:
        geometries = [
            Point(xy) for xy in zip(communities["longitude"], communities["latitude"])
        ]
        communities = gpd.GeoDataFrame(communities, geometry=geometries)
        iem_communities = communities.within(iem_gdf.geometry.unary_union)
        communities.loc[iem_communities, "tags"] = (
            communities.loc[iem_communities, "tags"] + ",ncr"
        )

        communities = communities.drop(columns="geometry")

    # Replace all nans with empty strings
    communities = communities.fillna("")

    # Convert back to a list of dicts
    new_csv = communities.to_dict("records")

    with open(f"tagged_csvs/{file}", "w") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(new_csv)
