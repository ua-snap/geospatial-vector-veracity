# `polygon` contents

Here are descriptions of the polygon vector data directories found in this subfolder.

## `boundaries`
Political or administrative boundaries of various administrative levels: country, state/province, land ownership, parks, etc.

## `symmetric_differences`
These are "shadow masks" that are essentially the inverse of another column and are useful for masking the area of valid queries (e.g. we can use these to "gray out" areas outside the domain for which data exists).

## `watersheds`
Organized by HUC level (e.g. HUC-8) for the United States.
