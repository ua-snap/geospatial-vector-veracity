"""
This utility will create a "shadow mask" of a polygon. This is effectively the inverse of the polygon where the input polygon will have no features, but features will populate the rest of the bounding box. In GIS lingo this is the "symmetric difference. This utility may fail for some geometries or where the number of feautres is large."
"""
import sys
import argparse
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon


def cmdline_args():
    """Create the command line parser object."""
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "input",
        type=str,
        help="Shapefile input filepath. Required.",
    )
    p.add_argument(
        "feature_name",
        type=str,
        help="Descriptive name for new polygon feature.",
    )
    p.add_argument(
        "feature_id",
        type=str,
        help="Unique alphanumeric ID for new polygon feature.",
    )
    p.add_argument(
        "output",
        type=str,
        help="Shapefile output filepath. Required.",
    )
    p.add_argument(
        "png_output",
        type=str,
        help="Image preview output filepath. Required.",
    )
    return p.parse_args()


def read_shapefile(shp_in):
    """Read shapefile to GeoDataFrame"""
    gdf = gpd.read_file(shp_in)
    return gdf


def get_extent(gdf):
    """Fetch extent of input shapefile"""
    extent = tuple(gdf.bounds.values[0])
    return extent


def make_bbox_polygon(long0, lat0, long1, lat1):
    """Create bounding box Polygon geometry from extent coordinates"""
    bbox_poly = Polygon([[long0, lat0], [long1, lat0], [long1, lat1], [long0, lat1]])
    return bbox_poly


def make_bbox_geodataframe(bbox_poly, crs):
    """Create GeoDataFrame from bounding box Polygon"""
    d = {"geometry": bbox_poly}
    bbox_gdf = gpd.GeoDataFrame(d, crs=crs, index=[0])
    return bbox_gdf


def compute_symmetric_difference(gdf, bbox_gdf):
    """Perform symmetric difference operatior and store results in a GeoDataFrame"""
    sym_diff = gpd.GeoDataFrame(
        gdf.symmetric_difference(bbox_gdf), columns=["geometry"], crs=gdf.crs
    )
    return sym_diff


def add_id_and_name(sym_diff, feature_id, feature_name):
    """Add identifying information to results GeoDataFrame"""
    sym_diff["id"] = feature_id
    sym_diff["name"] = feature_name


def save_symm_diff(sym_diff, out_filepath):
    """Save to new shapefile"""
    sym_diff.to_file(out_filepath)


def save_preview_png(sym_diff, out_filepath):
    """Save .png preview image for conventient inspection."""
    sym_diff.plot(figsize=(8, 5))
    plt.savefig(out_filepath, dpi=144, bbox_inches="tight")


if __name__ == "__main__":

    if sys.version_info < (3, 5, 0):
        sys.stderr.write("You need python 3.5 or later to run this script\n")
        sys.exit(1)

    try:
        args = cmdline_args()
        gdf = read_shapefile(args.input)
        extent = get_extent(gdf)
        bbox_poly = make_bbox_polygon(*extent)
        bbox_gdf = make_bbox_geodataframe(bbox_poly, gdf.crs)
        sym_diff = compute_symmetric_difference(gdf, bbox_gdf)
        add_id_and_name(sym_diff, args.feature_id, args.feature_name)
        save_symm_diff(sym_diff, args.output)
        save_preview_png(sym_diff, args.png_output)
    except:
        print(
            "Try python utilities/symmetric_difference.py vector_data/polygon/boundaries/iem/AIEM_domain.shp 'IEM Domain Symmetric Difference' 'XIEM1' IEM_symmetric_difference.shp preview.png"
        )
