import argparse
import os
from pathlib import Path

import pandas as pd
import rasterio as rio
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from rasterio.warp import transform_bounds, transform
from shapely.geometry import Point


def load_community_data(csv_path):
    """Load community point locations from a CSV file.

    Args:
        csv_path (pathlib.Path): Path to the CSV file containing community point locations.
    Returns:
        pd.DataFrame: DataFrame containing community point locations
    """
    df = pd.read_csv(csv_path)
    # if testing you can do something like return df[df["name"] == "Wainwright"]
    return df


def filter_out_communities_not_in_raster_bounds(community_df, raster_path):
    """Filter out communities outside raster bounds.

    Args:
        community_df (pd.DataFrame): DataFrame containing community point locations.
        raster_path (pathlib.Path): Path to the raster file.
    Returns:
        pd.DataFrame: DataFrame containing community point locations within raster bounds.
    """
    with rio.open(raster_path) as src:
        bounds = src.bounds
        bounds = transform_bounds(src.crs, "EPSG:4326", *bounds)
    # CP note - this wouldn't handle a literal edge case where community is just outside the edge of the raster, though you could pad the bounds below if desired
    return community_df[
        (community_df["latitude"] >= bounds[1])
        & (community_df["latitude"] <= bounds[3])
        & (community_df["longitude"] >= bounds[0])
        & (community_df["longitude"] <= bounds[2])
    ]


def transform_row_col_to_latlon(affine_transform, row, col):
    """Transform raster row/col to latitude and longitude.

    Args:
        affine_transform (Affine): Affine transform object
        row (int): Raster row
        col (int): Raster column
    Returns:
        tuple: (latitude, longitude)
    """
    # first go from row to col to pixel center coordinates for 3338
    x, y = rio.transform.xy(affine_transform, row, col, offset="center")
    # then go from 3338 to 4326
    lon, lat = transform("EPSG:3338", "EPSG:4326", [x], [y])
    return lat[0], lon[0]


def transform_row_col_to_projected_xy(affine_transform, row, col):
    """Transform raster row/col to latitude and longitude.

    Args:
        affine_transform (Affine): Affine transform object
        row (int): Raster row
        col (int): Raster column
    Returns:
        tuple: (projected x coord, projected y coord)
    """
    # first go from row to col to pixel center coordinates for 3338
    x, y = rio.transform.xy(affine_transform, row, col, offset="center")
    return x, y


def read_windowed_raster(src, community_coords, condition_values, window_size_m=2**15):
    """Read a window centered on the community coordinates.

    Args:
        src (rio.io.DatasetReader): rio dataset reader object
        community_coords (tuple): (latitude, longitude) for the community
        condition_values (list): List of values, one of which a raster grid cell must have to be considered a nearest neighbor
        window_size_m (int): Size of the window in meters. Default is 2^15.
    Returns:
        list: List of coordinates of raster grid cells that meet the condition"""
    # convert community lat/lon to EPSG:3338
    x, y = transform(
        "EPSG:4326", "EPSG:3338", [community_coords[1]], [community_coords[0]]
    )
    x = x[0]
    y = y[0]
    # use rio.windows.from_bounds(left, bottom, right, top) to make a window centered on the community, doing windowed reads speeds this up quite a bit
    window = rio.windows.from_bounds(
        x - window_size_m // 2,
        y - window_size_m // 2,
        x + window_size_m // 2,
        y + window_size_m // 2,
        src.transform,
    )
    raster = src.read(1, window=window, masked=True)
    affine_transform = src.window_transform(window)
    # we only want pixels that are ocean or ice
    mask = np.isin(raster, condition_values)
    rows, cols = np.where(mask)
    # all possible nearest neighbor coordinates
    coordinates = [
        transform_row_col_to_projected_xy(affine_transform, row, col)
        for row, col in zip(rows, cols)
    ]
    if DEBUG:
        # write the windowed raster for debugging
        output_path = f"debug/window_{community_coords[0]}_{community_coords[1]}.tif"
        window_meta = src.meta.copy()
        window_meta.update(
            {
                "driver": "GTiff",
                "height": window.height,
                "width": window.width,
                "transform": affine_transform,
            }
        )
        with rio.open(output_path, "w", **window_meta) as dst:
            dst.write(raster, indexes=1)
        # write the coordinates to a shapefile for debugging
        output_path = f"debug/coords_{community_coords[0]}_{community_coords[1]}.shp"
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(coord) for coord in coordinates]}, crs="EPSG:3338"
        )
        # only write if not empty
        if not gdf.empty:
            gdf.to_file(output_path)
    return coordinates


def find_nearest_neighbors(community_df, raster_path, condition_values, N):
    """
    Find the N nearest raster cell coordinates for each community within a windowed read.

    Args:
        community_df (pd.DataFrame): DataFrame containing community point locations.
        raster_path (pathlib.Path): Path to the raster file.
        condition_values (list): List of values, one of which a raster grid cell must have to be considered a nearest neighbor
        N (int): Number of nearest neighbors to find
    Returns:
        pd.DataFrame: DataFrame containing community point locations with nearest neighbors added.
    """
    results = []

    with rio.open(raster_path) as src:
        for _, community in community_df.iterrows():
            community_coords = (community["latitude"], community["longitude"])
            comm_x, comm_y = transform(
                "EPSG:4326", "EPSG:3338", [community_coords[1]], [community_coords[0]]
            )
            comm_x = comm_x[0]
            comm_y = comm_y[0]

            print(f"Finding nearest neighbors for {community['name']}...")
            coordinates = read_windowed_raster(src, community_coords, condition_values)

            if not coordinates:
                # If no valid coordinates are found in the window, create dummy result
                result = {}
                for i in range(N):
                    result[f"NN{i+1}_y"] = (None, None)
                    result[f"NN{i+1}_x"] = (None, None)
                results.append(result)
                continue

            # prepare KDTree with coordinates from the windowed read
            # CP note: basically n-dimensional binary search tree, see https://youtu.be/Glp7THUpGow
            coordinate_arr = np.array([[x, y] for x, y in coordinates])
            tree = cKDTree(coordinate_arr)
            distances, indices = tree.query([(comm_x, comm_y)], k=N)
            distances = distances[0]
            indices = indices[0]

            result = {}
            for i in range(N):
                if N == 1:
                    nearest_coord = coordinates[indices]
                else:
                    nearest_coord = coordinates[indices[i]]
                # nearest_coord = coordinates[indices[i]]
                result[f"NN{i+1}_x"] = round(nearest_coord[0], 1)
                result[f"NN{i+1}_y"] = round(nearest_coord[1], 1)
            results.append(result)

            if DEBUG:
                # write the nearest neighbors to a shapefile for debugging
                output_path = f"debug/neighbors_{community['name']}.shp"
                # result has structure {'NN1_x': 396968.1, 'NN1_y': 2267342.4,..
                gdf = gpd.GeoDataFrame(
                    {
                        "geometry": [
                            Point(result[f"NN{i+1}_x"], result[f"NN{i+1}_y"])
                            for i in range(N)
                        ]
                    },
                    crs="EPSG:3338",
                )
                if not gdf.empty:
                    gdf.to_file(output_path)

    # convert to df and concatenate with original df
    results_df = pd.DataFrame(results)
    updated_community_df = pd.concat(
        [community_df.reset_index(drop=True), results_df], axis=1
    )
    return updated_community_df


def save_updated_csv(df, output_path):
    """Save the updated DataFrame to a CSV file."""
    df.to_csv(output_path, index=False)
    print(f"Nearest neighbors added to the CSV and saved as '{output_path}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find nearest raster neighbors for community points. Example usage to find the 8 nearest neighbors for each community point in 'community.csv' using the raster 'raster.tif' and create shapefiles of the results: python find_nearest_raster_neighbors.py community.csv raster.tif output.csv --N 8 --DEBUG"
    )
    parser.add_argument(
        "community_csv_path",
        type=str,
        help="Path to the CSV file containing community point locations.",
    )
    parser.add_argument("raster_path", type=str, help="Path to the raster file.")
    parser.add_argument(
        "output_csv_path",
        type=str,
        help="Path to save the output CSV file with nearest neighbors.",
    )
    parser.add_argument(
        "--condition_value",
        type=int,
        nargs="+",
        default=[0, 255],
        help="Values which a raster grid cell must have to be considered a nearest neighbor. Default is 0 or 255.",
    )
    parser.add_argument(
        "--N",
        type=int,
        default=1,
        help="Number of nearest neighbors to find. Default is 1.",
    )
    parser.add_argument(
        "--DEBUG",
        action="store_true",
        help="Create debugging directory and write shapefiles of nearest neighbors and nearest neighbor candidates. Also write the raster subsets used in the search.",
    )
    args = parser.parse_args()
    community_csv_path = Path(args.community_csv_path)
    raster_path = Path(args.raster_path)
    output_csv_path = Path(args.output_csv_path)
    condition_value = args.condition_value
    N = args.N
    DEBUG = args.DEBUG
    if DEBUG:
        os.makedirs("./debug/", exist_ok=True)

    community_df = load_community_data(community_csv_path)
    community_df = filter_out_communities_not_in_raster_bounds(
        community_df, raster_path
    )
    updated_community_df = find_nearest_neighbors(
        community_df, raster_path, condition_value, N
    )
    save_updated_csv(updated_community_df, output_csv_path)
