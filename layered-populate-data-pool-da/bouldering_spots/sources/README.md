# 📂 Data Sources for Bouldering Spots

## OpenStreetMap (OSM)

* Source: https://wiki.openstreetmap.org/wiki/OpenStreetMap_API
* Update frequency: Unknown
* Data type: Dynamic (API)
* Relevant OSM Tag: `climbing:boulder=yes`

### Raw Data Sources

#### 📄 `bouldering_spots.geojson`

* Source: https://overpass-turbo.eu/
* Format: GeoJSON
* Description: Raw bouldering spot data extracted from OpenStreetMap using Overpass API.

#### 📄 `bouldering_spots.json`

* Source: https://overpass-turbo.eu/
* Format: JSON
* Description: Raw bouldering spot data extracted from OpenStreetMap using Overpass API, converted to JSON format.

#### 🔗 Overpass API Query

```
[out:json][timeout:25];
// manually define the area by name and admin level (Berlin is level 4)
area["name"="Berlin"]["admin_level"="4"]->.searchArea;

nwr["climbing:boulder"="yes"](area.searchArea);

out geom;
```

#### 🔗 OSM API Query using OSMnx Library

```python
import osmnx as ox

tags = {"climbing:boulder": "yes"}

bouldering_spots_df = ox.features_from_place("Berlin, Germany", tags=tags)
```

## Planned Transformation

1. **Raw Data Extraction**: Fetch raw bouldering spot data from OpenStreetMap using OSMnx.
2. **Data Cleaning**: Remove duplicates, and filter out irrelevant data.
4. **Geocoding**: Convert addresses to latitude and longitude coordinates.
5. **Gemoetry Conversion**: Convert `POLYGON()` geometries to `POINT()` format by using their centroid.
6. **Reverse Geolocation**: Get full address from coordinates.
7. **Convert and Validate Data Types**: Convert data types to ensure consistency and accuracy matching the final schema.
8. **Spatial Join**: Assign district and neighborhood.
9. **Finalize Columns**: Define final columns and their data types.
10. **Quality Checks**: Perform data quality checks to ensure data integrity and consistency.
11. **Geospatial Boundary Validation**: Ensure that all store coordinates fall within Berlin’s expected geographic boundaries.
11. **Export**: Export transformed data into a CSV file.
12. **Upload**: Upload the final dataset to a new database table.

## Table Schema

| Column Name       | Data Type                                            | Description                                                                                                           |
|-------------------|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| `id`              | `VARCHAR(20) NOT NULL`                               | Unique identifier for each bouldering spot (inherited OSM ID)                                                         |
| `district_id`     | `VARCHAR(20) NOT NULL`                               | ID of the district, foreign key to `districts(district_id)`                                                           |
| `neighborhood_id` | `VARCHAR(20)`                                        | ID of the neighborhood                                                                                                |
| `name`            | `VARCHAR(200) NOT NULL DEFAULT 'unknown_bouldering'` | Name of the bouldering spot, `unknown_bouldering` if missing                                                          |
| `latitude`        | `NUMERIC(9, 6)`                                      | Latitude                                                                                                              |
| `longitude`       | `NUMERIC(9, 6)`                                      | Longitude                                                                                                             |
| `geometry`        | `VARCHAR`                                            | Location of the spot in WKT `POINT()` format                                                                          |
| `neighborhood`    | `VARCHAR(100)`                                       | Name of the neighborhood the spot is in                                                                               |
| `district`        | `VARCHAR(100)`                                       | Name of the district the spot is in                                                                                   |
| `is_indoor`       | `BOOLEAN`                                            | Flag where `TRUE` means the spot has an indoor area                                                                   |
| `is_outdoor`      | `BOOLEAN`                                            | Flag where `TRUE` means the spot has an outdoor area                                                                  |
| `address`         | `VARCHAR(500)`                                       | Reverse geocoded address of the spot, derived from the coordinates                                                    |
| `street`          | `VARCHAR(200)`                                       | Street the spot is in                                                                                                 |
| `house_number`    | `VARCHAR(20)`                                        | House number of the spot                                                                                              |
| `postal_code`     | `VARCHAR(20)`                                        | Postal code of the spot                                                                                               |
| `pricing`         | `VARCHAR(20)`                                        | Pricing model for the spot. Currently only `Entry Fee` or `NULL`                                                      |
| `accessibility`   | `VARCHAR(50)`                                        | Accessibility of the spot (`Wheelchair accessible`, `Not wheelchair accessible`, `Limited wheelchair access`, `NULL`) |
| `opening_hours`   | `VARCHAR(255)`                                       | Opening hours                                                                                                         |
| `phone`           | `VARCHAR(100)`                                       | Phone number if available                                                                                             |
| `email`           | `VARCHAR(255)`                                       | Mail address if available                                                                                             |
| `website`         | `VARCHAR(255)`                                       | Website URL if available                                                                                              |
| `data_source`     | `VARCHAR(20)`                                        | Source of the data entry (currently only `OSM`)                                                                       |