# Bouldering Spots — Layered DB Table Info

## Table Overview

- **Schema:** `berlin_source_data`
- **Table:** `bouldering_spots`
- **Environment:** Development
- **Description:**  
  Contains cleaned and normalized bouldering spots data for Berlin, enriched with district
  and neighborhood references, intended for downstream analytics and applications.

Each row represents a single bouldering spot with geographic, descriptive,
and operational attributes.

---

## Columns

| Column Name       | Data Type                                            | Example Values                            | Description                                                                                                           |
|-------------------|------------------------------------------------------|-------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| `id`              | `VARCHAR(20) NOT NULL`                               | `1066131768`                              | Unique identifier for each bouldering spot (inherited OSM ID)                                                         |
| `district_id`     | `VARCHAR(20) NOT NULL`                               | `11006006`                                | ID of the district, foreign key to `districts(district_id)`                                                           |
| `neighborhood_id` | `VARCHAR(20)`                                        | `0604`                                    | ID of the neighborhood                                                                                                |
| `name`            | `VARCHAR(200) NOT NULL DEFAULT 'unknown_bouldering'` | `Boulderfelsen`                           | Name of the bouldering spot, `unknown_bouldering` if missing                                                          |
| `latitude`        | `NUMERIC(9, 6)`                                      | `52.413943`                               | Latitude                                                                                                              |
| `longitude`       | `NUMERIC(9, 6)`                                      | `13.264761`                               | Longitude                                                                                                             |
| `geometry`        | `VARCHAR`                                            | `POINT (13.264761 52.413943)`             | Location of the spot in WKT `POINT()` format                                                                          |
| `neighborhood`    | `VARCHAR(100)`                                       | `Zehlendorf`                              | Name of the neighborhood the spot is in                                                                               |
| `district`        | `VARCHAR(100)`                                       | `Steglitz-Zehlendorf`                     | Name of the district the spot is in                                                                                   |
| `is_indoor`       | `BOOLEAN`                                            | `false`                                   | Flag where `TRUE` means the spot has an indoor area                                                                   |
| `is_outdoor`      | `BOOLEAN`                                            | `false`                                   | Flag where `TRUE` means the spot has an outdoor area                                                                  |
| `address`         | `VARCHAR(500)`                                       | `Boulderfelsen, Werner-Sylten-Weg, [...]` | Reverse geocoded address of the spot, derived from the coordinates                                                    |
| `street`          | `VARCHAR(200)`                                       | `Ohlauer Straße`                          | Street the spot is in                                                                                                 |
| `house_number`    | `VARCHAR(20)`                                        | `38`                                      | House number of the spot                                                                                              |
| `postal_code`     | `VARCHAR(20)`                                        | `10999`                                   | Postal code of the spot                                                                                               |
| `pricing`         | `VARCHAR(20)`                                        | `Entry Fee`                               | Pricing model for the spot. Currently only `Entry Fee` or `Unknown`                                                   |
| `accessibility`   | `VARCHAR(50)`                                        | `Limited wheelchair access`               | Accessibility of the spot (`Wheelchair accessible`, `Not wheelchair accessible`, `Limited wheelchair access`, `NULL`) |
| `opening_hours`   | `VARCHAR(255)`                                       | `Mo-Fr 08:00-23:00; Sa-Su 10:00-22:00`    | Opening hours                                                                                                         |
| `phone`           | `VARCHAR(100)`                                       | `+49 1628195990`                          | Phone number if available                                                                                             |
| `email`           | `VARCHAR(255)`                                       | `basement@urbanapes.de`                   | Mail address if available                                                                                             |
| `website`         | `VARCHAR(255)`                                       | `https://derkegel.de/`                    | Website URL if available                                                                                              |
| `data_source`     | `VARCHAR(20)`                                        | `OSM`                                     | Source of the data entry (currently only `OSM`)                                                                       |

---

## Keys & Constraints

- **Primary Key**
  - `id`

**Foreign Key Constraint: `fk_bouldering_district`**
- Links `bouldering_spots.district_id` → `districts.district_id`
- **ON DELETE RESTRICT**: Prevents deletion of a district if any bouldering spots reference it. This protects against orphaned records and ensures data integrity.
- **ON UPDATE CASCADE**: Automatically propagates district_id changes from the districts table to all related bouldering spots. This maintains referential consistency across the database when district identifiers are updated.

---

## Data Sources

- **Primary:** OpenStreetMap (`climbing:boulder=yes` tag)
- **Geographic context:** Berlin administrative boundaries

---

## Load & Update Strategy

- Loaded via `bouldering_spots/scripts/bouldering_spots_data_transformation.ipynb`
- One-time batch insert into development database
- No automated refresh scheduled yet
- Intended for downstream consumption by analytics and recommender layers

---

## Validation

The following checks are applied during load:
- Row count verification
- Primary key uniqueness
- District and neighborhood foreign key validation
- Coordinates validation
