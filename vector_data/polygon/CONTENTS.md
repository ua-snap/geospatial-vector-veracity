# `polygon` contents

Here are descriptions of the polygon vector data directories found in this subfolder.

## `ak_protected_areas`
Boundaries for Alaska protected areas (Parks, Refuges, Reserves, etc.) created by the Commission for Environmental Cooperation (CEC) and published in 2010 as part of larger pan-North America dataset. A protected area is an “area of land and/or sea especially dedicated to the protection and maintenance of biological diversity, and of natural and associated cultural resources, and managed through legal or other effective means. 

## `boundaries`
Political or administrative boundaries of various administrative levels: country, state/province, land ownership, parks, etc.

## `symmetric_differences`
These are "shadow masks" that are essentially the inverse of another column and are useful for masking the area of valid queries (e.g. we can use these to "gray out" areas outside the domain for which data exists).

## `watersheds`
Organized by HUC level (e.g. HUC-8) for the United States.
