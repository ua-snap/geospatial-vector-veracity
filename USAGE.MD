# Usage

We're adding this section because we want to avoid manual editing of vector data that isn't reversible or reproducible whenever possible.

So, if possible...

## Use the scripts in the `utilities` directory.

You'll likely need to run these scripts from the same directory they reside in because we have some strict expectations about where files should be, and these expectations are hard-coded to enforce our required structure.

### `add_point_location.py`

Use this script to add new point locations to a point location CSV file. You should use this script because it will help ensure proper indexing, formatting, and coordinate precision. And indexing matters, because many of our tools map the `id` of a community to a URL specific to the data for that location (e.g., https://northernclimatereports.org/report/community/AK13#results) and we don't want those to shift.

### `convert_small_polygons_to_points.py`

Use this script converts polygons smaller than 10 km² to points and adds them to a points CSV file. This script exists because doing zonal statistics with small polygons and gridded datasets with coarse spatial resolutions is not useful. For example, if the grid spatial resolution is 4 km², then a 10 km² polygon will have a zonal mean computed from ~2 grid cell values. Instead, it is better to track these small polygons as points so they can be included in point queries. The small polygons are removed from the source shapefile and are migrated to a point geometry represented by the centroid coordinates of the input polygons.

Example usage:

```sh
python convert_small_polygons_to_points.py \
    --polygons ../vector_data/polygon/boundaries/protected_areas/bc_protected_areas/bc_protected_areas.shp \
    --points ../vector_data/point/british_columbia_point_locations.csv \
```

### `compute_distance_to_coastline.py`

This script computes the distance to the nearest coastline for a list of communities. The script will create or update a column in the input CSV file with the distance to the nearest coastline in kilometers. A column `is_coastal` will also be created or updated to indicate whether the community is coastal or not based on some threshold distance, for which the default is 100 km. The script will iterate through all CSV files in the `../vector_data/point` directory and update each file with the new distance and coastal tag.

### `create_shapefiles.py`

This script creates updated versions of shapefiles on GeoServer for various geographical boundaries and communities. First it loads community point geometries while renaming columns to adhere to the ESRI Shapefile format's 10-character limit. Attu is specifically kicked out of the community list. A schema for the output shapefile is defined and a new filtered community points shapefile is written. Next the polygonal boundaries (watersheds, boroughs, census areas, climate divisions, protected areas,etc.) are 4326-ified if they aren't already in that CRS, and BC and YT protected areas are filtered to retain only those within the IEM AOI. All these geographical areas are then merged into a single DataFrame, with unnecessary metadata columns dropped. The merged DataFrame is written to a new shapefile. Finally, the script generates a separate shapefile for HUC12 areas, setting their type and CRS before saving them to a file.

### `symmetric_difference.py`

Use this script to create a "shadow mask" of a polygon - this effectively generates a feature that is the inverse of the polygon within a bounding box. We often use such "shadow masks" as web map elements to visually guide the user where valid queries do and do not exist. We dim the lights where there isn't data.

### `find_nearest_raster_neighbors.py`

A utility for finding the nearest raster grid cells that meet certain conditions for a set of community point locations. The script uses a CSV file with community lat-lon coordinates and a GeoTIFF and identifies the N closest raster grid cell neighbors for each point using a combination of windowed raster reads and a k-d tree. The resulting nearest neighbor coordinates represent the center of the raster grid cells and are added to the input CSV file. Run with `--DEBUG` to write interim shapefiles and raster subsets for detailed inspection. An example usage of this script to generate a single nearest sea ice atlas neighbor for all community CSVs is:

```sh
for csv in ../vector_data/point/*_point_locations.csv; do
    echo "Processing $csv..."
    python find_nearest_raster_neighbors.py "$csv" hsia_mask.tif --grid_cell_values 1 --N 1
done
```

### `simplify_huc12.py`

More of a one-off, this script reads a source shapefile `wbdhu12_a_ak.shp` of AK HUC-12s and converts it to EPSG:3338 and simplifies the geometries (tolerance of 100 m) while preserving topology to ensure that the simplified geometries do not overlap or create invalid shapes. A few specific HUC12s are also dropped from the resulting dataset because they were deemed poor "data cookie cutters" for our purposes.

### `crop_aiem_domain.py`

This script removes extraneous polygon feature blobs from the `AIEM_domain.shp` file that are outside the actual IEM domain. This is a one-off, and actually probably doesn't need to be tracked, but is dumped here for posterity.

### `tag_point_locations.py`

This script reads point location CSVs from the `vector_data/point` directory and then adds (or overwrites) the "tags" column in each CSV. The "tags" column is a comma-separated list of webapps that the community should be included in. This includes communities that are exclusive to Arctic-EDS, communities that are contained by the IEM AOI for Northern Climate Reports, and nearly all Alaska + international communities to be included in ARDAC Explorer. Tagged CSVs are written to the `utilities/tagged_csvs` directory for review.
