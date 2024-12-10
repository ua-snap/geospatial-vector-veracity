"""
This utility is used to add tags to the "tags" column of point location CSV
files. It will overwrite any existing tag in the tags column currently, but we
can modify this script to be more sophisticated as needed. The scirpt outputs
the tagged CSVs to a new directory called "tagged_csvs", from where they can be
copied into the vector_data/point directory.
"""

import os
import csv
import geopandas as gpd

file_tags = {
    "alaska_point_locations.csv": ["ncr", "eds", "ardac"],
    "alberta_point_locations.csv": [],
    "british_columbia_point_locations.csv": ["ncr"],
    "manitoba_point_locations.csv": [],
    "northwest_territories_point_locations.csv": [],
    "saskatchewan_point_locations.csv": [],
    "yukon_point_locations.csv": ["ncr"],
}

if not os.path.exists("tagged_csvs"):
    os.makedirs("tagged_csvs")

for root, dirs, files in os.walk("../vector_data/point"):
    for file in files:
        if file.endswith(".csv"):
            with open(os.path.join(root, file), "r") as f:
                new_csv = []
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                if "tags" not in fieldnames:
                    fieldnames.append("tags")
                for row in reader:
                    tags = file_tags[file]
                    new_row = row.copy()
                    new_row["tags"] = ",".join(tags)
                    new_csv.append(new_row)
                with open(f"tagged_csvs/{file}", "w") as f:
                    writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
                    writer.writeheader()
                    writer.writerows(new_csv)
