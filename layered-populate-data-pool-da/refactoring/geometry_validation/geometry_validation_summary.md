# Final Report: Berlin POI Geometry & Schema Audit

**Date:** January 2026  
**Analyst:** Anny Llosa  
**Scope:** Validation of 44 POIs tables within the `berlin_source_data` schema.

**Project: Berlin POI Geometry & Coordinate Validation**



## 1. Executive Summary


This audit provides a technical evaluation of Berlin's POI datasets. While the data is structurally valid, significant issues were identified regarding data redundancy (duplicates), mixed geometry types, and spatial boundary violations. The use of explicit casting was essential to uncover these hidden inconsistencies within the `geometry` columns



## 2. Key Findings


**A. Structural & Schema Observations**

- **Storage Format**: Not all geometries are stored as `character varying`. There are 15 tables that use either native PostGIS types (USER_DEFINED) or standard text.

| # | table_name | column_name | data_type |
|---|---|---|---|
| 0 | bike_lanes | geometry | USER-DEFINED |
| 1 | bus_stops | geometry | USER-DEFINED |
| 2 | districts | geometry | USER-DEFINED |
| 3 | government_offices | geometry | USER-DEFINED |
| 4 | gyms | geometry | USER-DEFINED |
| 5 | job_centers | geometry | text |
| 6 | libraries | geometry | USER-DEFINED |
| 7 | long_term_listings | geometry | text |
| 8 | milieuschutz_protection_zones | geometry | USER-DEFINED |
| 9 | neighborhoods | geometry | USER-DEFINED |
| 10 | schools | geometry | text |
| 11 | short_term_listings | geometry | USER-DEFINED |
| 12 | social_clubs_activities | geometry | text |
| 13 | spaetis | geometry | text |
| 14 | tram_stops | geometry | USER-DEFINED |
  
- **Mixed Geometries (Critical)**: There are several tables with with records in 'geometry' that have diffebt format than 'ST_POINT':

| # | table_name | detected_type | total_records |
|---|---|---|---|
| 0 | bike_lanes | ST_MultiLineString | 78833 |
| 1 | districts | ST_MultiPolygon | 12 |
| 2 | job_centers | ST_Polygon | 163 |
| 3 | milieuschutz_protection_zones | ST_MultiPolygon | 1754 |
| 4 | neighborhoods | ST_MultiPolygon | 96 |
| 5 | parking_spaces | ST_Polygon | 53232 |
| 6 | parking_spaces | ST_LineString | 20 |
| 7 | parking_spaces | ST_MultiPolygon | 255510 |
| 8 | short_term_listings | ST_MultiPolygon | 14187 |

- **Geometry Integrity**: All records passed the `ST_IsValid` check, meaning there are no "broken" WKT strings.

- **Coordinate Precision Issues**:
Requirement: Coordinates (lat/lon) should be DECIMAL(9,6)/NUMERIC(9,6).

There are several tables that do not meet these requirenments:

| table_name | column_name | data_type | numeric_precision | numeric_scale |
| :--- | :--- | :--- | :--- | :--- |
| banks | longitude | numeric | 10 | 6.0 |
| banks | latitude | numeric | 10 | 6.0 |
| food_markets | latitude | numeric | 10 | 7.0 |
| food_markets | longitude | numeric | 10 | 7.0 |
| job_centers | latitude | double precision | 53 | NaN |
| job_centers | longitude | double precision | 53 | NaN |
| milieuschutz_protection_zones | longitude | numeric | 10 | 6.0 |
| milieuschutz_protection_zones | latitude | numeric | 10 | 6.0 |


**B. Spatial & Coordinate Validation(Outliers)**

Despite the current storage format, a deep spatial validation was performed via explicit casting, producing the following results:

- Latitude / Longitude Range: While the majority of records fall within the expected Berlin range, a targeted audit revealed tables with coordinates that fall outside the logical boundaries of the study area:

| # | table_name | points_outside |
|---|---|---|
| 0 | bike_lanes | 92 |
| 1 | long_term_listings | 12 |
| 2 | milieuschutz_protection_zones | 43 |
| 3 | neighborhoods | 364 |
| 4 | parking_spaces | 305 |
| 5 | short_term_listings | 782 |

- Geometry Parsing: All geometry strings were successfully parsed using `ST_GeomFromText(geometry, 4326)` confirming that the text-based storage hasn't corrupted the underlying data points.

- Point-in-Polygon (Boundary) Check: Using the `districts` layer as the official reference, the audit found that not all data is 100% consistent.

  - Coverage is missing (0 records) for districts like Spandau and Steglitz-Zehlendorf in the parking dataset, indicating data gaps.

- Missing Data: bike_lanes contains 78,833 records with missing coordinate data.



