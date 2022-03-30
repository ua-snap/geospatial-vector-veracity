# geospatial-vector-veracity
Veracious geospatial vector data for use in SNAP tools.

## What is this?
This repository is a place to store geospatial vector data (i.e. points, lines, and polygons) that has been validated for geographic accuracy and for place name orthography.

## Why does this exist?
In the past we've encountered vector data that did not meet SNAP standards of excellence. For example:
 - Incorrect locations off by up to ten degrees of longitude.
 - Outdated place names such as Trout Lake, NT (now Sambaa K’e, NT).
 - Place names that lack special characters or are sourced from files that lack the encoding for those characters, e.g. Utiagvik vs. **Utqiaġvik**.
 - Ambiguous place names such as Moose Creek, Alaska

Geography is not static. Names change, places shift, locations grow and diminish in prominence, and even fade away and dissapear.

This repository is intended to resolve and mitigate these issues and to serve as the One True Source of GIS vector data for usage in SNAP tools and datasets.

## Scope
### Vector Geometries
 - Now:
     + points (e.g. communities, airports, mines, military installations).
     + polygons (e.g. administrative units, watersheds, cultural and physical boundaries).
 - Maybe in the future: lines (e.g. roads, pipelines).

### Geographic Extent
 - Alaska and Western Canada

## Beyond Scope
 - This is not a complex geodatabase.
 - Non-geographic data (e.g. population).
 - This should not be considered an authoritative resource, especially with respect to Indigenous place names.
 - This is not a complete or "official" resource for vector data.

## Data Model
### Points
 - Unique and concise alphanumeric `id` field serves as the index.
 - Minimal set of geographic fields / columns.
 - Coordinates extend to 4 digits of precision. 4 is the number and the number shall be 4.
 - No spatially redundant points to the extent possible (i.e., points should be greater than ~1 km apart).

Like so:

| id   | name     | alt_name      | region   | country   |   latitude |   longitude |   km_distance_to_ocean |
|:-----|:---------|:--------------|:---------|:----------|-----------:|------------:|-----------------------:|
| AK1  | Afognak  | Agw’aneq      | Alaska   | US        |    58.0078 |    -152.768 |                    0.2 |
| AK2  | Akhiok   | Kasukuak      | Alaska   | US        |    56.9455 |    -154.17  |                    0.1 |
| AK3  | Akiachak | Akiacuar      | Alaska   | US        |    60.9094 |    -161.431 |                   89.7 |
| AK4  | Akiak    | Akiaq         | Alaska   | US        |    60.9122 |    -161.214 |                   97.4 |
| AK5  | Akutan   | Achan-ingiiga | Alaska   | US        |    54.1385 |    -165.778 |                    0.6 |

### Polygons
In this repo polygons features serve as map elements (think domains for individual projects) and/or as "data cookie cutters" that can summarize various gridded datasets over some area.
#### Some caveats for the latter case:
 - For small (less than ~10 km<sup>2</sup> in area) polygons track them as points instead.
 - For discontinuous polygons consider splitting them into individual features or dropping entirely if appropriate.
 - For polygons with interior holes consider filling them in if appropriate.
 - For polygons that are otherwise sporadic, bizzare, or span some massive extent (e.g., the entire Alaskan coastline) just drop the feature entirely.
 
#### General guidance
  - Strive to keep file sizes under 100 MB.
  - In that spirit, consider simplifying geometries to some reasonable level.
  - Validate geometries.
  - As with points, keeps the fields / columns short, tight, and sparse and supply a unique alphanumeric `id` to serve as the index.
  
Like so:

| id     | name                                      | region   | country   | area_type                                     | geometry                                          |
|:-------|:------------------------------------------|:---------|:----------|:----------------------------------------------|:--------------------------------------------------|
| USFS1  | Admiralty Island National Monument        | Alaska   | USA       | National Monument (USFS)                      | MULTIPOLYGON (((1144020.440 998268.375, 114401... |
| AKDNR1 | Afognak Island State Park                 | Alaska   | USA       | State Park                                    | MULTIPOLYGON (((112741.762 907629.893, 112720.... |
| NPS1   | Alagnak Wild River                        | Alaska   | USA       | National River & Wild & Scenic Riverway (NPS) | MULTIPOLYGON (((-122946.125 1004423.139, -1233... |
| AKDNR2 | Alaska Chilkat Bald Eagle Preserve        | Alaska   | USA       | State Nature Preserve                         | MULTIPOLYGON (((1025214.965 1174326.030, 10252... |
| FWS3   | Alaska Peninsula National Wildlife Refuge | Alaska   | USA       | National Wildlife Refuge (FWS)                | MULTIPOLYGON (((-600067.304 576372.255, -60005... |
