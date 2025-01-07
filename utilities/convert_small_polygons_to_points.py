"""
This script converts area polygons smaller than 10 km² to points and adds them 
to a points CSV file using the add_point_location utility. The reason this script exists is because doing zonal statistics over small polygons with respect to the spatial resolution of most of the SNAP datasets is not useful. For example, if a spatial resolution is 4 km², then a 10 km² polygon will have a value for every 4 km² cell in the dataset. A zonal mean would then be the mean of ~2 grid cell values, which is not useful. Instead, we track these small polygons as points.

Example usage:
    python convert_small_polygons_to_points.py \
        --shapefile ../vector_data/polygon/boundaries/protected_areas/bc_protected_areas/bc_protected_areas.shp \
        --points-csv ../vector_data/point/british_columbia_point_locations.csv \
        --proj-epsg 3005 \
        --region BC \
        --country CA
"""

import os
import sys
import argparse
import geopandas as gpd
import pandas as pd

# we want to import from add_point_location to make sure we have integrity with how points should be added
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from add_point_location import get_last_id_number_in_df, create_new_id


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert small polygons to points and add them to a points CSV file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--shapefile",
        type=str,
        required=True,
        help="Path to input shapefile containing polygons",
    )
    parser.add_argument(
        "--points-csv",
        type=str,
        required=True,
        help="Path to points CSV to add new points to",
    )
    parser.add_argument(
        "--proj-epsg",
        type=int,
        required=True,
        help="EPSG code for projected coordinate system to use for area calculations",
    )
    parser.add_argument(
        "--region",
        type=str,
        required=True,
        help="Region code (e.g., BC for British Columbia)",
    )
    parser.add_argument(
        "--country",
        type=str,
        required=True,
        help="Country code (e.g., CA for Canada)",
    )
    parser.add_argument(
        "--max-area",
        type=float,
        default=10.0,
        help="Maximum area in square kilometers (default: 10)",
    )
    parser.add_argument(
        "--tags",
        type=str,
        default="ardac",
        help="Comma-separated tags to apply to new points (default: ardac)",
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


def add_points_to_csv(points_gdf, points_df, region, country, tags, csv_path):
    """Add new points to points CSV file."""
    # get the last ID number to start incrementing from, this is important so we don't muck up the existing IDs
    last_id = get_last_id_number_in_df(points_df)

    # create new records
    new_records = []
    for idx, row in points_gdf.iterrows():
        last_id += 1
        new_id = create_new_id(region, last_id)

        new_record = {
            "id": new_id,
            "name": row["name"],
            "alt_name": "",  # could be populated if alternative names exist, but unlikelky for polygons
            "region": region,
            "country": country,
            "latitude": round(row.geometry.y, 4),
            "longitude": round(row.geometry.x, 4),
            "tags": tags,
        }
        new_records.append(new_record)
        print(f"Adding {new_record['name']} as {new_id}")

    # create DataFrame of new records and combine with existing points
    new_df = pd.DataFrame(new_records)
    combined_df = pd.concat([points_df, new_df], ignore_index=True)
    combined_df = combined_df.sort_values("name")
    combined_df.to_csv(csv_path, index=False)
    print(f"\nWrote {len(new_records)} new records to {csv_path}")


def update_shapefile(large_polygons, shapefile_path):
    """Write updated shapefile with small polygons removed."""
    # convert back to original CRS if needed
    original_gdf = gpd.read_file(shapefile_path)
    if large_polygons.crs != original_gdf.crs:
        large_polygons = large_polygons.to_crs(original_gdf.crs)

    # Write the filtered polygons back to the shapefile
    # All original attributes are preserved since we never modified them
    large_polygons.to_file(shapefile_path)
    print(
        f"\nUpdated {shapefile_path} - removed {len(original_gdf) - len(large_polygons)} small polygons"
    )


def main():
    args = parse_arguments()

    polygons = load_polygons(args.shapefile, args.proj_epsg)
    points = load_points(args.points_csv)
    small_polygons, large_polygons = calculate_areas_and_filter(polygons, args.max_area)
    point_features = convert_to_points(small_polygons)
    add_points_to_csv(
        point_features, points, args.region, args.country, args.tags, args.points_csv
    )
    update_shapefile(large_polygons, args.shapefile)

    print(f"Converted {len(point_features)} small polygons to points")


if __name__ == "__main__":
    main()
