"""
This script converts polygons smaller than 10 km² to points and adds them 
to a points CSV file. This script exists because doing zonal statistics with small polygons and gridded datasets with coarse spatial resolutions is not useful. For example, if the grid spatial resolution is 4 km², then a 10 km² polygon will have a zonal mean computed from ~2 grid cell values. Instead, it is better to track these small polygons as points so they can be included in point queries.

Example usage:
    python convert_small_polygons_to_points.py \
        --polygons ../vector_data/polygon/boundaries/protected_areas/bc_protected_areas/bc_protected_areas.shp \
        --points ../vector_data/point/british_columbia_point_locations.csv \
"""

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd

# we want to import from add_point_location to make sure we have integrity with how points should be added
from add_point_location import get_last_id_number_in_df, create_new_id, postal_di
from crs_lookup import crs_lookup
# reverse keys and values in postal_di
postal_di = {v: k for k, v in postal_di.items()}


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--polygons",
        type=str,
        required=True,
        help="Path to input shapefile containing polygons",
    )
    parser.add_argument(
        "--points",
        type=str,
        required=True,
        help="Path to points CSV to add new points to",
    )
    parser.add_argument(
        "--max-area",
        type=float,
        default=10.0,
        help="Maximum area in square kilometers (default: 10)",
    )
    return parser.parse_args()


def load_polygons(shapefile_path, proj_epsg):
    """Load polygons from shapefile and ensure proper projection."""
    gdf = gpd.read_file(shapefile_path)
    # projected space for area calculation
    if gdf.crs.is_geographic or gdf.crs.to_epsg() != proj_epsg:
        gdf = gdf.to_crs(f"EPSG:{proj_epsg}")
    return gdf


def load_points(csv_path):
    """Load existing points CSV."""
    return pd.read_csv(csv_path)


def calculate_areas_and_filter(gdf, max_area_km2=10):
    """Calculate areas and filter for polygons smaller than max_area_km2."""
    # Add area calculation as a temporary column
    gdf["_area_km2"] = gdf.geometry.area / 1_000_000  # Convert m² to km²

    # Filter but preserve all original columns
    small_polygons = gdf[gdf["_area_km2"] < max_area_km2].copy()
    large_polygons = gdf[gdf["_area_km2"] >= max_area_km2].copy()

    # Remove temporary area column
    small_polygons = small_polygons.drop(columns=["_area_km2"])
    large_polygons = large_polygons.drop(columns=["_area_km2"])

    return small_polygons, large_polygons


def convert_to_points(small_polygons):
    """Convert polygons to points using centroids."""
    points = small_polygons.copy()
    points.geometry = points.geometry.centroid
    # Convert to WGS84 for lat/lon coordinates
    points = points.to_crs("EPSG:4326")
    return points


def create_new_records(points_gdf, points_df):

    # get the last ID number to start incrementing from, this is important so we don't muck up the existing IDs
    last_id = get_last_id_number_in_df(points_df)

    # point files are split by region and country, so we can just grab the first record
    region = points_df["region"].iloc[0]
    country = points_df["country"].iloc[0]
    id_prefix = postal_di[region]

    # create new records
    new_records = []
    for idx, row in points_gdf.iterrows():
        new_id = create_new_id(id_prefix, last_id)

        new_record = {
            "id": new_id,
            "name": row["name"],
            "alt_name": None, # add manually on ad hoc basis later if needed
            "region": region,
            "country": country,
            "latitude": round(row.geometry.y, 4),
            "longitude": round(row.geometry.x, 4),
            "tags": None, # will be populated in tagging script
            "km_distance_to_ocean": None, # will be populated in coastal script
            "is_coastal": None, # will be populated in coastal script
            "ocean_lat1": None, # ocean coords will be populated in neighbor script
            "ocean_lon1": None, # ocean coords will be populated in neighbor script
        }
        new_records.append(new_record)
        print(f"Adding {new_record['name']} as {new_id}")
        last_id += 1

    new_df = pd.DataFrame(new_records)
    return new_df

def merge_existing_and_new_points(existing_points, new_points):
    """Merge existing points with new points."""
    combined_df = pd.concat([existing_points, new_points], ignore_index=True)
    combined_df.sort_values("name", inplace=True)
    return combined_df


def write_new_csv(combo_df, csv_path):
    """Write new points CSV."""
    combo_df.to_csv(csv_path, index=False)


def drop_small_polygons(original_polygons, small_polygons):
    """Drop small polygons by the dataframe column called "id"."""
    filtered_polys = original_polygons[~original_polygons["id"].isin(small_polygons["id"])]
    return filtered_polys

def update_shapefile(filtered_polygons, shapefile_path):
    """Write updated shapefile with small polygons removed."""
    filtered_polygons.to_file(shapefile_path, encoding="utf-8")


def main():
    args = parse_arguments()
    
    region_name = Path(args.points).name.split("_point_locations")[0]
    existing_points = load_points(args.points)
    proj_crs = crs_lookup[region_name]
    polygons = load_polygons(args.polygons, proj_crs)

    small_polygons, large_polygons = calculate_areas_and_filter(polygons, args.max_area)
    
    new_points = convert_to_points(small_polygons)
    new_records = create_new_records(new_points, existing_points)
    merged = merge_existing_and_new_points(existing_points, new_records)
    
    updated_polys = drop_small_polygons(polygons, small_polygons)
    
    write_new_csv(merged, args.points)
    
    update_shapefile(updated_polys, args.polygons)

    print(f"Converted {len(new_points)} small polygons to points")


if __name__ == "__main__":
    main()