# `boundaries` contents

Here are descriptions of the polygon vector data found in this subfolder.

| filename | description | source | feature count |
|---|---|---|---|
| `alaska_coast_simplified/Alaska_Coast_Simplified_Polygon.shp` | Coastline for the state of Alaska at a scale of 1:63,360 | [State of Alaska Geoportal](https://gis.data.alaska.gov/datasets/alaska-simplified-coast/explore) | 177 |
| `boroughs/ak_boroughs.shp` | Outlines Alaska borough administrative units. Fetched August 2022. | [State of Alaska Geoportal](https://gis.data.alaska.gov/datasets/DCCED::alaska-borough-and-census-area-boundaries/about#) | 19 |
| `census_areas/ak_census_areas.shp` | Outlines of the Alaska census areas that compose the Unorganized Borough. Fetched August 2022. | [State of Alaska Geoportal](https://gis.data.alaska.gov/datasets/DCCED::alaska-borough-and-census-area-boundaries/about#) | 11 |
| `fire/ak_fire_mgmt/ak_fire_management.shp` | Outlines of Alaska Fire Management Zones. Fetched August 2022. | [Alaska Interagency Coordination Center](https://fire.ak.blm.gov/content/maps/aicc/Data/Data%20(zipped%20Shapefiles)/WildCAD_Zones_2021.zip) | 14 |
| `fire/yt_firemgmt/yt_fire_management.shp` | Outlines of Yukon Fire Districts. Fetched August 2022. | [GeoYukon](https://map-data.service.yukon.ca/GeoYukon/Administrative_Boundaries/Fire_Districts/Fire_Districts.shp.zip) | 13 |
| `game_management_units/ak_gmus/ak_gmu.shp` | Outlines of Alaska Game Management Subunits. Fetched April 2022. | [Alaska Department of Fish and Game](https://adfg.maps.arcgis.com/home/item.html?id=f1019b8731aa4ec4921501d035c7ba5e&_ga=2.105278848.2020792229.1649708106-1267992404.1647486331) | 72 |
| `game_management_units/yt_gmzs/yt_game_management_zones.shp` | Outlines of Yukon Game Management Subzones. These only have numeric identifiers, they do not have a true name, so the `name` field is given by `zone-subzone`, e.g., 11-30 indicates Zone 11, Subzone 28. Sometimes the subzones are also called game management areas. Polygons have been cross-referenced with this map(https://map-data.service.yukon.ca/GeoYukon/Administrative_Boundaries/Game_Management_Areas_250k/Game_Management_Areas_250k.shp.zip). These polygons span the Yukon with the exception of the National Parks. Fetched August 2022. | [GeoYukon](https://map-data.service.yukon.ca/GeoYukon/Administrative_Boundaries/Game_Management_Areas_250k/Game_Management_Areas_250k.shp.zip) | 443 |
| `iem/AIEM_Domain.shp` | Outline of the domain for the IEM project. Spans Alaska, the Yukon, and parts of northern British Columbia. | [USGS ScienceBase Entry](https://www.sciencebase.gov/catalog/item/5a3009a1e4b08e6a89d57bc6) | 1 |
