from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree


def calculate_coastal_distances(point_locations_path):
    """
    Calculate the distance of each point to the nearest coastline in kilometers.

    Args:
        point_locations_path (str): Path to the CSV file containing point locations.

    Returns:
        pd.DataFrame: A DataFrame with the original data and a new or updated column for the distance to the coastline.
    """
    communities_df = pd.read_csv(Path(point_locations_path))
    geometry = gpd.points_from_xy(communities_df.longitude, communities_df.latitude)
    communities_gdf = gpd.GeoDataFrame(
        communities_df, geometry=geometry, crs="EPSG:4326"
    )
    # reproject to 3338 because ideally we compute distances in projected space
    communities_gdf = communities_gdf.to_crs("EPSG:3338")

    coast_gdf = gpd.read_file(
        Path(
            "../vector_data/polygon/boundaries/natural_earth_global_coastlines/ne_10m_coastline.shp"
        )
    )
    # crop coastline to only include features between 40°N and 84°N, this is not strictly necessary but it does reduce the search space
    coast_gdf = coast_gdf[
        (coast_gdf.geometry.bounds.miny >= 40) & (coast_gdf.geometry.bounds.maxy <= 84)
    ]
    coast_gdf = coast_gdf.to_crs("EPSG:3338")

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
    community_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    for point_locations_path in Path("../vector_data/point").glob("*.csv"):
        communities_df = calculate_coastal_distances(point_locations_path)
        communities_df = add_coastal_tag(communities_df)
        write_to_csv(communities_df, point_locations_path)
