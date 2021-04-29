# geospatial-vector-veracity
Veracious geospatial vector data for use in SNAP tools.

## What is this?
This repository is a place to store geospatial vector data (i.e. points, lines, and polygons) that has been validated for geographic accuracy and for place name orthography.

## Why does this exist?
At times, vector data did not meet SNAP standards of excellence. For example:
 - Incorrect locations off by up to ten degrees of longitude.
 - Outdated place names such as Trout Lake, NWT (now Sambaa K’e, NWT).
 - Place names that lack special characters or are sourced from files that lack the encoding for those characters, e.g. Utiagvik vs. **Utqiaġvik**.
 - Ambiguous place names such as Moose Creek, Alaska

Geography is not static. Names change, places shift, locations grow and diminish in prominence, and even fade away and dissapear.

This repository is intended to resolve and mitigate these issues and serve as the One True Source of GIS vector data for usage in SNAP tools and datasets.

## Scope
### Vector Geometries
 - Now: points (e.g. communities, airports, mines).
 - Next: polygons (e.g. administrative units, watersheds).
 - Maybe: lines (e.g. roads, pipelines).

### Geographic Extent
 - Alaska and Western Canada

## Beyond Scope
 - This is not a complex geodatabase.
 - Non-geographic data (e.g. population).
 - External use (for now). This should not be considered an authoritative resource, especially with respect to Indigenous place names.

## Data Model
Like so:

|  | name | alt_name | region | country | latitude | longitude |
|-|-|-|-|-|-|-|
| 0 | Aklavik | NaN | Northwest Territories | CA | 68.2200 | -135.0087 |
| 1 | Behchokǫ̀ | Rae-Edzo | Northwest Territories | CA | 62.8335 | -116.0514 |
| 2 | CanTung Mine | NaN | Northwest Territories | CA | 61.9717 | -128.2683 |
| 3 | Colville Lake | K'áhbamį́túé | Northwest Territories | CA | 67.0399 | -126.0912 |
| 4 | ConocoPhillips EL470 Base Camp | NaN | Northwest Territories | CA | 65.0534 | -127.0355 |

