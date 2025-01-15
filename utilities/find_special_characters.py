import os
import csv
import geopandas as gpd


# Return true if any special (non-ASCII) characters are found in the string
def characters_special(string):
    return any(ord(char) > 127 for char in string)


print("##### Special characters in CSV files:")
for root, dirs, files in os.walk("../vector_data/point"):
    for file in files:
        if file.endswith(".csv"):
            with open(os.path.join(root, file), "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if characters_special(row["name"]) or characters_special(
                        row["alt_name"]
                    ):
                        print(row["id"], row["name"], row["alt_name"])

print("\n##### Special characters in shapefiles:")
excluded_shapefiles = [
    "Alaska_Coast_Simplified_Polygon.shp",
    "iem_with_ak_aleutians.shp",
    "AIEM_domain.shp",
    "IEM_symmetric_difference.shp",
    "iem_with_ak_aleutians_symmetric_difference.shp",
]

for root, dirs, files in os.walk("../vector_data/polygon"):
    for file in files:
        if file in excluded_shapefiles:
            continue
        if file.endswith(".shp"):
            gdf = gpd.read_file(os.path.join(root, file))
            for feature in gdf["name"]:
                if characters_special(feature):
                    print(file, feature)
