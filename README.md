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
     + polygons (e.g. administrative units, watersheds).
 - Maybe in the future: lines (e.g. roads, pipelines).

### Geographic Extent
 - Alaska and Western Canada

## Beyond Scope
 - This is not a complex geodatabase.
 - Non-geographic data (e.g. population).
 - This should not be considered an authoritative resource, especially with respect to Indigenous place names.

## Data Model
Like so:

| id  | name     | alt_name            | region | country | latitude | longitude |
|-----|----------|---------------------|--------|---------|----------|-----------|
| AK1 | Afognak  | Agw'aneq            | Alaska | US      | 58.0078  | -152.768  |
| AK2 | Akhiok   | Kasukuak            | Alaska | US      | 56.9455  | -154.17   |
| AK3 | Akiachak | Akiacuaq / Akiacuar | Alaska | US      | 60.9094  | -161.431  |
| AK4 | Akiak    | Akiaq               | Alaska | US      | 60.9122  | -161.214  |
| AK5 | Akutan   | Achan-ingiiga       | Alaska | US      | 54.1385  | -165.778  |
