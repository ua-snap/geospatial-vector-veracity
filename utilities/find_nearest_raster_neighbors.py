import pandas as pd
import rasterio as rio
import numpy as np
from scipy.spatial import cKDTree
from rasterio.windows import Window
from rasterio.warp import transform_bounds, transform
from geopy.distance import geodesic
import multiprocessing as mp


def load_community_data(csv_path):
    """Load community point locations from a CSV file."""
    return pd.read_csv(csv_path)


def filter_out_communities_not_in_raster_bounds(community_df, raster_path):
    """Filter out communities outside raster bounds."""
    with rio.open(raster_path) as src:
        bounds = src.bounds
        bounds = transform_bounds(src.crs, "EPSG:4326", *bounds)

    return community_df[
        (community_df["latitude"] >= bounds[1])
        & (community_df["latitude"] <= bounds[3])
        & (community_df["longitude"] >= bounds[0])
        & (community_df["longitude"] <= bounds[2])
    ]


def read_windowed_raster(src, community_coords, condition_values, window_size=512):
    """Read a 1024x1024 window centered on the community coordinates."""
    # Convert community lat/lon to raster row/column
    x, y = transform("EPSG:4326", src.crs, [community_coords[1]], [community_coords[0]])
    col, row = src.index(x[0], y[0])

    # Define window boundaries with the community point in the middle of the bottom row of the window

    window = Window(col - window_size // 2, row - window_size, window_size, window_size)
    raster = src.read(1, window=window, masked=True)
    affine_transform = src.window_transform(window)  # Renamed to avoid conflict
    mask = np.isin(raster, condition_values)

    shift_step = window_size // 2
    while mask.sum() == 0 and window.row_off - shift_step >= 0:
        window = Window(
            window.col_off, window.row_off - shift_step, window.width, window.height
        )
        raster = src.read(1, window=window, masked=True)
        affine_transform = src.window_transform(window)
        mask = np.isin(raster, condition_values)

    print(mask.sum())

    rows, cols = np.where(mask)
    coordinates = [
        transform_to_latlon(affine_transform, src.crs, row, col)
        for row, col in zip(rows, cols)
    ]
    return coordinates


def transform_to_latlon(affine_transform, crs, row, col):
    """Transform raster row/col to latitude and longitude."""
    x, y = rio.transform.xy(affine_transform, row, col, offset="center")
    lon, lat = transform("EPSG:3338", "EPSG:4326", [x], [y])
    return lat[0], lon[0]


def find_nearest_neighbors(community_df, raster_path, condition_values, N):
    """
    Find the N nearest raster cell coordinates for each community within a windowed read.
    """
    results = []

    with rio.open(raster_path) as src:
        for _, community in community_df.iterrows():
            community_coords = (community["latitude"], community["longitude"])
            print(f"Finding nearest neighbors for {community['name']}...")
            # Extract raster coordinates within a 1024x1024 window centered on the community location
            coordinates = read_windowed_raster(src, community_coords, condition_values)

            if not coordinates:
                # If no valid coordinates are found in the window, create a result with None values
                result = {f"NN{i+1}": (None, None) for i in range(N)}
                result.update({f"NN{i+1}_dist_km": None for i in range(N)})
                results.append(result)
                continue

            # Prepare KDTree with coordinates from the windowed read
            lat_lons = np.array([[lat, lon] for lat, lon in coordinates])
            tree = cKDTree(lat_lons)

            # Find the N nearest neighbors
            distances, indices = tree.query([community_coords], k=N)
            distances = distances[0]
            indices = indices[0]

            # Structure results
            result = {}
            for i in range(N):
                nearest_coord = coordinates[indices[i]]
                distance_km = geodesic(community_coords, nearest_coord).kilometers
                result[f"NN{i+1}"] = nearest_coord
                result[f"NN{i+1}_dist_km"] = round(distance_km, 4)
            results.append(result)

    # Convert results to DataFrame and concatenate with original DataFrame
    results_df = pd.DataFrame(results)
    updated_community_df = pd.concat(
        [community_df.reset_index(drop=True), results_df], axis=1
    )

    return updated_community_df


def save_updated_csv(community_df, output_path):
    """Save the updated DataFrame to a CSV file."""
    community_df.to_csv(output_path, index=False)
    print(f"Nearest neighbors added to the CSV and saved as '{output_path}'.")


if __name__ == "__main__":
    # Configuration (could later be CLI arguments)
    community_csv_path = "../vector_data/point/alaska_point_locations.csv"
    raster_path = "beaufort_19961222_radarsat_slie.tif"
    output_csv_path = "nn_locations.csv"
    condition_value = [0, 255]  # Values of interest in raster cells
    N = 8  # Number of nearest neighbors to find

    # Load and filter community data
    community_df = load_community_data(community_csv_path)
    community_df = filter_out_communities_not_in_raster_bounds(
        community_df, raster_path
    )

    # Find nearest neighbors and save to CSV
    updated_community_df = find_nearest_neighbors(
        community_df, raster_path, condition_value, N
    )
    save_updated_csv(updated_community_df, output_csv_path)
