# `polygon` contents

## Brief descriptions of the polygon vector data found here.

```
polygon
├── boundaries
│   ├── alaska_coast_simplified
│   ├── alaska_hucs
│   ├── boroughs
│   ├── census_areas
│   ├── climate_divisions
│   ├── corporation
│   ├── ecoregions
│   ├── ethnolinguistic
│   ├── fire
│   │   ├── ak_fire_mgmt
│   │   └── yt_fire_mgmt
│   ├── first_nations
│   ├── game_management_units
│   │   ├── ak_gmus
│   │   └── yt_gmzs
│   ├── iem
│   ├── iem_with_ak_aleutians
│   ├── natural_earth_global_coastlines
│   ├── protected_areas
│   │   ├── ak_protected_areas
│   │   ├── bc_protected_areas
│   │   └── yt_protected_areas
│   └── yt_watersheds
└── symmetric_differences
    ├── iem
    └── iem_with_ak_aleutians
```

## `boundaries`

Political or administrative or physical boundaries including land ownership and management units, parks, refuges, fire management boundaries, ethnolinguistic regions, native corporations, coastlines, and climate divisions.

### `alaska_coast_simplified`

Simplified EPSG:3338 geometry of the otherwise complex and crenulated AK coastline. Don't use this for anything that requires high precision like masking or clipping high resolution gridded data because coastal locations may experience data loss. Fetched from the [State of Alaska's Geoportal in January 2025](https://gis.data.alaska.gov/maps/SOA-DNR::alaska-coastline/about).

### `alaska_hucs`

Alaska hydrologic units (i.e., watersheds) organized by hydrologic unit code (HUC) level (e.g. HUC-8) for Alaska. Available data include HUC-12, HUC-10, and HUC-8 polygons. The Alaska HUC datasets are not exact copies of official USGS data. In some instances polygons have been removed or simplified to enhance their application for web mapping and geospatial operations involving gridded datasets with spatial resolutions ranging between 0.5 km and 20 km.

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

### `ecoregions`

EPA Level 3 Ecoregions for Alaska.

### `fire`

Management zones (which agency / office is responsible for wildfire). These are not physical data.

### `first_nations`

First Nations. The geographic extent is Yukon and the CRS is WGS84. An appropriate projection is Yukon Albers EPSG 3578.

### `game_management_units`

Alaska Game Management Subunits from the Alaska Department of Fish and Game.

### `iem`

The spatial domain of the Integrated Ecosystem Modeling (IEM) project. Alaska excluding the Aleutians, plus some of Yukon and British Columbia (it is complicated).

### `iem_with_ak_aleutians`

As above, but with the Aleutians this time :)

### `natural_earth_global_coastlines`

Global coastline data from Natural Earth. Used to determine the distance to the nearest coastline for communities.

### `protected_areas`

Boundaries for protected areas in Alaska and western Canada (Parks, Refuges, Reserves, etc.) created by the Commission for Environmental Cooperation (CEC) and published in 2010 as part of larger pan-North America dataset. A protected area is an “area of land and/or sea especially dedicated to the protection and maintenance of biological diversity, and of natural and associated cultural resources, and managed through legal or other effective means." Organized by state, territory, or province.

## `symmetric_differences`

These are "shadow masks" that are essentially the inverse of another column and are useful for masking the area of valid queries (e.g. we can use these to "gray out" areas outside the domain for which data exists).

### References

1.  Bieniek, P. A., Bhatt, U. S., Thoman, R. L., Angeloff, H., Partain, J., Papineau, J., Fritsch, F., Holloway, E., Walsh, J. E., Daly, C., Shulski, M., Hufford, G., Hill, D. F., Calos, S., & Gens, R. (2012). Climate Divisions for Alaska Based on Objective Methods, Journal of Applied Meteorology and Climatology, 51(7), 1276-1289. [doi: 10.1175/JAMC-D-11-0168.1](https://www.doi.org/10.1175/JAMC-D-11-0168.1)
