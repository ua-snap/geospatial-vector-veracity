# geospatial-vector-veracity

Veracious geospatial vector data for use in SNAP tools.

## What is this?

This repository is a place to store geospatial vector data (i.e. points, lines, and polygons) that has been validated for geographic accuracy and for place name orthography.

## Why does this exist?

In the past we've encountered vector data that did not meet SNAP quality standards. For example:

- Incorrect locations off by up to ten degrees of longitude.
- Outdated place names such as Trout Lake, NT (now Sambaa K’e, NT).
- Place names that lack special characters or are sourced from files that lack the encoding for those characters, e.g. Utiagvik vs. **Utqiaġvik**.
- Ambiguous place names such as Moose Creek, Alaska

This repository is intended to resolve and mitigate these issues and to serve as the One True Source of GIS vector data for usage in SNAP tools and datasets.

## Scope

### Vector Geometries

- Now:
  - points (e.g. communities, airports, mines, military installations).
  - polygons (e.g. administrative units, watersheds, cultural and physical boundaries).
- Maybe in the future: lines (e.g. roads, pipelines).

### Geographic Extent

- Pan-Arctic with an emphasis on Alaska

## Beyond Scope

- This is not a complex geodatabase.
- Non-geographic data (e.g. population).
- This is not an authoritative resource, especially with respect to Indigenous place names.
- This is not a complete or "official" resource for vector data.

## Data Model

### Points

- Unique and concise alphanumeric `id` field serves as the index.
- Minimal set of geographic fields / columns.
- Coordinates extend to 4 digits of precision. 4 is the number and the number shall be 4.
- No spatially redundant points to the extent possible (i.e., points should be greater than ~1 km apart).
- Alternate and/or Indigenous names included when confirmed with a trusted third party.
- A `tags` field to enable web applications to pull the appropriate point location sets.
- Geographic fields to facilitate use in SNAP web applications that reference coastal distance, coastal status and nearest ocean neighbor grid cell coordinates.

Example:

|     | id  | name     | alt_name      | region | country | latitude | longitude | tags          | km_distance_to_ocean | is_coastal | ocean_lat1 | ocean_lon1 |
| --: | :-- | :------- | :------------ | :----- | :------ | -------: | --------: | :------------ | -------------------: | :--------- | ---------: | ---------: |
|   0 | AK1 | Afognak  | Agw’aneq      | Alaska | US      |  58.0078 |  -152.768 | ardac,eds,ncr |                    1 | True       |    57.9202 |    -152.91 |
|   1 | AK2 | Akhiok   | Kasukuak      | Alaska | US      |  56.9455 |   -154.17 | ardac,eds,ncr |                  0.8 | True       |    57.0185 |   -154.305 |
|   2 | AK3 | Akiachak | Akiacuar      | Alaska | US      |  60.9094 |  -161.431 | ardac,eds,ncr |                 33.5 | True       |     60.433 |   -162.469 |
|   3 | AK4 | Akiak    | Akiaq         | Alaska | US      |  60.9122 |  -161.214 | ardac,eds,ncr |                   43 | True       |    60.4169 |   -162.583 |
|   4 | AK5 | Akutan   | Achan-ingiiga | Alaska | US      |  54.1385 |  -165.778 | ardac,eds,ncr |                  1.4 | True       |    54.1978 |   -165.923 |

### Polygons and MultiPolygons

These features serve as map elements for web applications and/or as "data cookie cutters" (i.e. inputs for zonal statistics) that summarize gridded datasets over a geographic area.

- Unique and concise alphanumeric `id` field serves as the index.
- Convert small polygons (less than ~10 km<sup>2</sup> in area) to points.
- Retain only the necessary descriptive fields in the attribute table.
- Simplify geometries as needed, but visually verify fidelity to original precision.
- Strive to keep file sizes under 100 MB.
- Ensure that geometries are valid

Example:

| id     | name                                      | region | country | area_type                                     | geometry                                          |
| :----- | :---------------------------------------- | :----- | :------ | :-------------------------------------------- | :------------------------------------------------ |
| USFS1  | Admiralty Island National Monument        | Alaska | USA     | National Monument (USFS)                      | MULTIPOLYGON (((1144020.440 998268.375, 114401... |
| AKDNR1 | Afognak Island State Park                 | Alaska | USA     | State Park                                    | MULTIPOLYGON (((112741.762 907629.893, 112720.... |
| NPS1   | Alagnak Wild River                        | Alaska | USA     | National River & Wild & Scenic Riverway (NPS) | MULTIPOLYGON (((-122946.125 1004423.139, -1233... |
| AKDNR2 | Alaska Chilkat Bald Eagle Preserve        | Alaska | USA     | State Nature Preserve                         | MULTIPOLYGON (((1025214.965 1174326.030, 10252... |
| FWS3   | Alaska Peninsula National Wildlife Refuge | Alaska | USA     | National Wildlife Refuge (FWS)                | MULTIPOLYGON (((-600067.304 576372.255, -60005... |
