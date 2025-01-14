import argparse
import os
import subprocess
from pathlib import Path

import pandas as pd
import rasterio as rio
import numpy as np
import geopandas as gpd
from scipy.spatial import cKDTree
from rasterio.warp import transform
from shapely.geometry import Point

from crs_lookup import crs_lookup


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


def transform_row_col_to_latlon(affine_transform, row, col, crs):
    """Transform raster row/col to latitude and longitude.

    Args:
        affine_transform (Affine): Affine transform object
        row (int): Raster row
        col (int): Raster column
        crs (int): EPSG code of the projected CRS to transform from
    Returns:
        tuple: (latitude, longitude)
    """
    # first go from row to col to pixel center coordinates for 3338
    x, y = rio.transform.xy(affine_transform, row, col, offset="center")
    # then go from 3338 to 4326
    lon, lat = transform(f"EPSG:{crs}", "EPSG:4326", [x], [y])
    return lat[0], lon[0]


def transform_row_col_to_projected_xy(affine_transform, row, col):
    """Transform raster row/col to x and y.

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


def prep_raster(raster_path, crs):
    """Reproject the raster to the appropriate projected CRS using a `gdalwarp` subprocess call. The new raster will be saved in the same directory as the original raster with the same filename but with a '_reprojected_crs' suffix.

    Args:
        raster_path (pathlib.Path): Path to the raster file.
        crs (int): EPSG code of the projected CRS to reproject to
    Returns:
        pathlib.Path: Path to the prepared raster file.
    """

    src_crs = rio.open(raster_path).crs
    if src_crs != f"EPSG:{crs}":
        reprojected_path = Path(
            str(raster_path).replace(".tif", f"_reprojected_{crs}.tif")
        )
        subprocess.run(
            ["gdalwarp", "-t_srs", f"EPSG:{crs}", raster_path, reprojected_path]
        )
        return reprojected_path
    else:
        return raster_path


def read_windowed_raster(
    src,
    band_number,
    crs,
    community_coords,
    grid_cells_vals,
    window_size_m=2**20,
    community_name=None,
):
    """Read a window centered on the community coordinates.

    Args:
        src (rio.io.DatasetReader): rio dataset reader object
        band_number (int): Number of the band to read
        crs (int): EPSG code of the projected CRS
        community_coords (tuple): (latitude, longitude) for the community
        grid_cells_vals (list): List of values, one of which a raster grid cell must match to be considered a nearest neighbor
        window_size_m (int): Size of the window in meters.
    Returns:
        list: List of coordinates of raster grid cells that meet the condition"""
    # convert community lat/lon to projected CRS coordinates
    x, y = transform(
        "EPSG:4326", f"EPSG:{crs}", [community_coords[1]], [community_coords[0]]
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

    raster = src.read(band_number, window=window, masked=True)
    affine_transform = src.window_transform(window)
    # we only want pixels that match certain values
    mask = np.isin(raster, grid_cells_vals)
    rows, cols = np.where(mask)
    # all possible nearest neighbor coordinates
    coordinates = [
        transform_row_col_to_projected_xy(affine_transform, row, col)
        for row, col in zip(rows, cols)
    ]
    if DEBUG:
        # write the windowed raster "chip" for debugging
        output_path = f"debug/window_{community_name}.tif"
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
        output_path = f"debug/coords_{community_name}.shp"
        gdf = gpd.GeoDataFrame(
            {"geometry": [Point(coord) for coord in coordinates]}, crs=f"EPSG:{crs}"
        )
        # only write if not empty
        if not gdf.empty:
            gdf.to_file(output_path)
    return coordinates


def find_nearest_neighbors(
    community_df,
    raster_path,
    band_number,
    grid_cells_vals,
    k_nearest_neighbors,
    label_prefix,
    crs,
):
    """
    Find the k nearest raster cell centroid coordinates for each community within a windowed read.

    Args:
        community_df (pd.DataFrame): DataFrame containing community point locations.
        raster_path (pathlib.Path): Path to the raster file.
        band_number (int): Number of the band to read from the raster file.
        grid_cells_vals (list): List of values, one of which a raster grid cell must have to be considered a nearest neighbor
        k_nearest_neighbors (int): Number of nearest neighbors to find
        label_prefix (str): Prefix to add to the column names for the nearest neighbor latitudes and longitudes
        crs (int): EPSG code of the projected CRS
    Returns:
        pd.DataFrame: DataFrame containing community point locations with nearest neighbors added.
    """
    results = []
    raster_path = prep_raster(raster_path, crs)
    with rio.open(raster_path) as src:
        for _, community in community_df.iterrows():
            community_coords = (community["latitude"], community["longitude"])
            comm_x, comm_y = transform(
                "EPSG:4326", f"EPSG:{crs}", [community_coords[1]], [community_coords[0]]
            )
            comm_x = comm_x[0]
            comm_y = comm_y[0]

            print(f"Finding nearest neighbors for {community['name']}...")
            coordinates = read_windowed_raster(
                src,
                band_number,
                crs,
                community_coords,
                grid_cells_vals,
                community_name=community["name"],
            )

            if not coordinates:
                # If no valid coordinates are found in the window, create dummy result
                result = {}
                for i in range(k_nearest_neighbors):
                    result[f"NN{i+1}_y"] = None
                    result[f"NN{i+1}_x"] = None
                results.append(result)
                continue

            # prepare KDTree with coordinates from the windowed read
            # CP note: basically n-dimensional binary search tree, see https://youtu.be/Glp7THUpGow
            coordinate_arr = np.array([[x, y] for x, y in coordinates])
            tree = cKDTree(coordinate_arr)
            distances, indices = tree.query([(comm_x, comm_y)], k=k_nearest_neighbors)
            distances = distances[0]
            indices = indices[0]

            result = {}
            for i in range(k_nearest_neighbors):
                if k_nearest_neighbors == 1:
                    nearest_coord = coordinates[indices]
                else:
                    nearest_coord = coordinates[indices[i]]
                result[f"NN{i+1}_x"] = nearest_coord[0]
                result[f"NN{i+1}_y"] = nearest_coord[1]

            gdf = gpd.GeoDataFrame(
                {
                    "geometry": [
                        Point(result[f"NN{i+1}_x"], result[f"NN{i+1}_y"])
                        for i in range(k_nearest_neighbors)
                    ]
                },
                crs=f"EPSG:{crs}",
            )
            gdf = gdf.to_crs("EPSG:4326")
            # for each nearest neighbor, create a column for the latitude and longitude and add the latitude and longitude value for that neighbor to the column
            for i in range(k_nearest_neighbors):
                gdf[f"{label_prefix}_lat{i+1}"] = gdf.geometry.y.iloc[i]
                gdf[f"{label_prefix}_lon{i+1}"] = gdf.geometry.x.iloc[i]
                result[f"{label_prefix}_lat{i+1}"] = round(
                    gdf[f"{label_prefix}_lat{i+1}"].iloc[0], 4
                )
                result[f"{label_prefix}_lon{i+1}"] = round(
                    gdf[f"{label_prefix}_lon{i+1}"].iloc[0], 4
                )
                # now drop the projected NN keys because we don't need them anymore
                result.pop(f"NN{i+1}_x")
                result.pop(f"NN{i+1}_y")

            results.append(result)

            if DEBUG:
                # write the nearest neighbors to a shapefile for debugging
                output_path = f"debug/neighbors_{community['name']}.shp"
                if not gdf.empty:
                    gdf.to_file(output_path)

    # convert to df and concatenate with original df
    results_df = pd.DataFrame(results)
    # drop any "NN" columns that might exist
    results_df = results_df.drop(
        columns=[col for col in results_df.columns if "NN" in col]
    )
    updated_community_df = pd.concat([community_df.reset_index(), results_df], axis=1)
    return updated_community_df


def save_updated_csv(df, output_path):
    """Save the updated DataFrame to a CSV file."""
    if "index" in df.columns:
        df = df.drop(columns=["index"])
    if DEBUG:
        df.to_csv(f"debug/{output_path.name}", index=False)
    else:
        df.to_csv(output_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find nearest raster neighbors for point locations. Example usage to find a single nearest neighbor for each point in 'community.csv' using a single band raster 'gridded_data.tif': python find_nearest_raster_neighbors.py community.csv gridded_data.tif --band_number 1 --N 1"
    )
    parser.add_argument(
        "community_csv_path",
        type=str,
        help="Path to the CSV file containing community point locations.",
    )
    parser.add_argument("raster_path", type=str, help="Path to the raster file.")
    parser.add_argument(
        "--band_number",
        type=int,
        default=1,
        help="Number of the band to read from the raster file. Default is 1.",
    )
    parser.add_argument(
        "--grid_cell_values",
        type=int,
        nargs="+",
        default=[1],
        help="A raster grid cell must have one of these values to be considered a nearest neighbor. Default is 1. Any number of values can be provided.",
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
    band_number = args.band_number
    grid_cell_values = args.grid_cell_values
    neighbors = args.N
    DEBUG = args.DEBUG

    if DEBUG:
        os.makedirs("./debug/", exist_ok=True)

    region_name = community_csv_path.name.split("_point_locations")[0]
    proj_crs = crs_lookup[region_name]

    print(f"Processing {region_name} with {proj_crs} projection...")

    community_df = load_community_data(community_csv_path)
    updated_community_df = find_nearest_neighbors(
        community_df,
        raster_path,
        band_number,
        grid_cell_values,
        neighbors,
        "ocean",
        proj_crs,
    )
    save_updated_csv(updated_community_df, community_csv_path)
