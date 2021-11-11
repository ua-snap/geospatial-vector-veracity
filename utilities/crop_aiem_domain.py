# This is what was used to remove a troublesome/extraneous blob
# int the original AIEM_domain.shp file that was 
# outside of the IEM domain.

import geopandas
from shapely.geometry import MultiPolygon


gdf = gpd.read_file("vector_data/polygon/boundaries/iem/AIEM_domain.shp")

# filter out if easternmost bound is east of 2000000 (arbitrary cutoff)
# tracker to make sure this is just one poly
tracker = []
new_polys = []
for poly in list(gdf.geometry[0].geoms):
    if poly.bounds[2] > 2000000:
        tracker.append(poly)
    else:
        new_polys.append(poly)


new_gdf = gdf.copy(deep=True)
new_gdf.geometry[0] = MultiPolygon(new_polys)

new_gdf.to_file("vector_data/polygon/boundaries/iem/AIEM_domain.shp")
