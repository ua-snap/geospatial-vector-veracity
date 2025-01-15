from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

from crs_lookup import crs_lookup


def calculate_coastal_distances(point_locations_path, projected_crs_code):
    """
    Calculate the distance of each point to the nearest coastline in kilometers.

    Args:
        point_locations_path (str): Path to the CSV file containing point locations.
        projected_crs_code (int): The EPSG code of the projected coordinate reference system to use for the distance calculation.

    Returns:
        pd.DataFrame: A DataFrame with the original data and a new or updated column for the distance to the coastline.
    """
    communities_df = pd.read_csv(Path(point_locations_path))
    geometry = gpd.points_from_xy(communities_df.longitude, communities_df.latitude)
    communities_gdf = gpd.GeoDataFrame(
        communities_df, geometry=geometry, crs="EPSG:4326"
    )
    # reproject to compute distances in projected space
    projected_crs = f"EPSG:{projected_crs_code}"
    communities_gdf = communities_gdf.to_crs(projected_crs)

    coast_gdf = gpd.read_file(
        Path(
            "../vector_data/polygon/boundaries/natural_earth_global_coastlines/ne_10m_coastline.shp"
        )
    )
    # crop coastline to only include features between 40°N and 84°N, this is not strictly necessary but it does reduce the search space
    coast_gdf = coast_gdf[
        (coast_gdf.geometry.bounds.miny >= 40) & (coast_gdf.geometry.bounds.maxy <= 84)
    ]
    coast_gdf = coast_gdf.to_crs(projected_crs)

    # convert coastline LineString geometries to array of coordinates, each LineString has numerous individual xy coordinates
    coast_coords = coast_gdf.geometry.apply(lambda x: list(x.coords))
    coast_coords = np.array([coord for coords in coast_coords for coord in coords])
    coast_coords = np.array(list(coast_coords))

    tree = cKDTree(coast_coords)
    community_coords = np.array([(p.x, p.y) for p in communities_gdf.geometry])
    # compute distances in meters and convert to km
    distances, _ = tree.query(community_coords)
    distances_km = (distances / 1000).round(1)

    communities_df["km_distance_to_ocean"] = distances_km
    return communities_df


def add_coastal_tag(community_df, coastal_distance_km_threshold=100):
    """
    Add a new column to the DataFrame indicating whether each point is coastal or not.

    Args:
        community_df (pd.DataFrame): The DataFrame containing the point locations and distances.
        coastal_distance_km_threshold (int): The distance threshold in kilometers.

    Returns:
        pd.DataFrame: The updated DataFrame with the new coastal tag column.
    """
    community_df["is_coastal"] = (
        community_df["km_distance_to_ocean"] < coastal_distance_km_threshold
    )
    return community_df


def write_to_csv(community_df, output_path):
    # if there is a column named "index" in the dataframe, drop it
    # this could be an artifact from the tree construction
    # sometimes in pandas you get a column named "index" that is not an actual `Index` object
    if "index" in community_df.columns:
        community_df = community_df.drop(columns=["index"])
    community_df.to_csv(output_path, index=False)


if __name__ == "__main__":

    for point_locations_path in Path("../vector_data/point").glob("*.csv"):
        # csv names are like newfoundland_and_labrador_point_locations.csv
        region_name = point_locations_path.name.split("_point_locations")[0]
        print(f"Processing {region_name}...")
        communities_df = calculate_coastal_distances(
            point_locations_path, crs_lookup[region_name]
        )
        communities_df = add_coastal_tag(communities_df)
        write_to_csv(communities_df, point_locations_path)
