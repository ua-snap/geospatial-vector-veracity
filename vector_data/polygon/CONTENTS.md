# `polygon` contents

Brief descriptions of the polygon vector data found here. Unless otherwise noted, expect EPSG:3338 projections.

```
polygon
├── boundaries
│   ├── alaska_coast_simplified
│   ├── alaska_hucs
|   ├── boroughs
│   ├── census_areas
│   ├── climate_divisions
│   ├── corporation
│   ├── ethnolinguistic
│   ├── fire
│   ├── first_nations
│   ├── iem
│   ├── iem_with_ak_aleutians
│   └── protected_areas
│       ├── ak_protected_areas
│       ├── bc_protected_areas
│       └── yt_protected_areas
└── symmetric_differences
    ├── iem
    └── iem_with_ak_aleutians
│   ├── yt_watersheds
```

## `boundaries`
Political or administrative boundaries including land ownership and management units, parks, refuges, fire management boundaries, ethnolinguistic regions, native corporations, and climate divisions.

### `alaska_coast_simplified`
Simplified EPSG:3338 geometry of the otherwise complex and crenulated AK coastline. Great for clipping raster data. This is the go-to AK spatial boundary polygon.

### `alaska_hucs`
Alaska hydrologic units (i.e., watersheds) organized by HUC level (e.g. HUC-8) for Alaska.

### `boroughs`
Alaska administrative boroughs - these are analogous to counties in the Lower 48. The Unorganized Borough (yes, that is the real name) is excluded because it is not a valid "data cookie cutter" because it is so large.

### `census_areas`
The eleven census areas that compose Alaska's Unorganized Borough. These areas do not have government of their own - they are used for statistics. Boroughs and census areas are both treated as county-level equivalents by the U.S. Census Bureau.

### `climate_divisions`
Peter Bieniek's (1) AK climate divisions, or how to chunk up Alaska by climate.

### `corporation`
Alaska Native Corporations.

### `ethnolinguistic`
Ethnographic / linguistic zones for Alaska and parts of Canada.

### `fire`
#### `ak_fire_mgmt`
Alaska fire management zones (which agency / office is responsible for wildfire).
#### `yt_fire_mgmt`
Yukon fire districts.

### `first_nations`
First Nations. The geographic extent is Yukon and the CRS is WGS84. An appropriate projection is Yukon Albers EPSG 3578.

### `game_management_units`
#### `ak_gmus`
Alaska Game Management Subunits from the Alaska Department of Fish and Game.
#### `yt_gmzs`
Yukon Game Management Subzones.

### `iem`
The spatial domain of the Integrated Ecosystem Modeling (IEM) project. Alaska excluding the Aleutians, plus some of Yukon and British Columbia (it is complicated).

### `iem_with_ak_aleutians`
As above, but with the Aleutians this time :)

### `protected_areas`
Boundaries for protected areas in Alaska and western Canada (Parks, Refuges, Reserves, etc.) created by the Commission for Environmental Cooperation (CEC) and published in 2010 as part of larger pan-North America dataset. A protected area is an “area of land and/or sea especially dedicated to the protection and maintenance of biological diversity, and of natural and associated cultural resources, and managed through legal or other effective means." Organized by state, territory, or province.

## `symmetric_differences`
These are "shadow masks" that are essentially the inverse of another column and are useful for masking the area of valid queries (e.g. we can use these to "gray out" areas outside the domain for which data exists).

## `yt_watersheds`
These are the Yukon hydrologic units that are similar to the HUCs used in the United States.

### References

1.  Bieniek, P. A., Bhatt, U. S., Thoman, R. L., Angeloff, H., Partain, J., Papineau, J., Fritsch, F., Holloway, E., Walsh, J. E., Daly, C., Shulski, M., Hufford, G., Hill, D. F., Calos, S., & Gens, R. (2012). Climate Divisions for Alaska Based on Objective Methods, Journal of Applied Meteorology and Climatology, 51(7), 1276-1289. [doi: 10.1175/JAMC-D-11-0168.1](https://www.doi.org/10.1175/JAMC-D-11-0168.1)
