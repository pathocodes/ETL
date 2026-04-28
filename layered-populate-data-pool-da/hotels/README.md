# Hotels — Layered DB Table Info

## Table Overview

- **Schema:** `berlin_source_data`
- **Table:** `hotels`
- **Environment:** Development
- **Description:**  
  Contains cleaned and normalized hotel data for Berlin, enriched with district
  and neighborhood references, intended for downstream analytics and applications.

Each row represents a single hotel entity with geographic, descriptive,
and operational attributes.

---

## Columns

| Column name        | Type           | Nullable | Example value                         | Description |
|--------------------|----------------|----------|---------------------------------------|-------------|
| id                 | VARCHAR(20)    | No       | `86001840`                            | Unique hotel identifier |
| district_id        | VARCHAR(20)    | No       | `11001001`                            | Foreign key reference to districts |
| neighborhood_id    | VARCHAR(20)    | Yes      | `0101`                                | Logical reference to neighborhoods |
| name               | VARCHAR(200)   | No       | `Hilton Berlin`                       | Hotel name |
| latitude           | DECIMAL(9,6)   | Yes      | `52.512103`                           | Latitude coordinate |
| longitude          | DECIMAL(9,6)   | Yes      | `13.392540`                           | Longitude coordinate |
| geometry           | VARCHAR        | Yes      | `POINT (13.3925395 52.5121031)`       | WKT point representation |
| neighborhood       | VARCHAR(100)   | Yes      | `Mitte`                               | Neighborhood name |
| district           | VARCHAR(100)   | Yes      | `Mitte`                               | District name |
| hotel_type         | VARCHAR(50)    | Yes      | `hotel`                               | Hotel category/type |
| star_rating        | INT            | Yes      | `5`                                   | Star rating (1–5) |
| amenities          | TEXT           | Yes      | `Smoking area, Wi-Fi`                 | Amenities list |
| accessibility      | VARCHAR(100)   | Yes      | `Wheelchair access`                   | Accessibility information |
| room_count         | INT            | Yes      | `601`                                 | Number of rooms |
| phone              | VARCHAR(100)   | Yes      | `+49 30 202 300`                      | Contact phone |
| website            | VARCHAR(200)   | Yes      | `https://www.hilton.com/en/hotels...` | Website URL |
| email              | VARCHAR(200)   | Yes      | `info.berlin@hilton.com`              | Contact email |
| address            | VARCHAR(200)   | Yes      | `Anton-Wilhelm-Amo-Straße 30, 10117`  | Full address |
| street             | VARCHAR(200)   | Yes      | `Anton-Wilhelm-Amo-Straße`            | Street name |
| house_number       | VARCHAR(50)    | Yes      | `30`                                  | House number |
| postal_code        | VARCHAR(20)    | Yes      | `10117`                               | Postal code |
| data_source        | TEXT           | Yes      | `osm`                                 | Source system |
| source_ids         | TEXT           | Yes      | `osm:86001840`                        | Raw source identifiers |



---

## Keys & Constraints

- **Primary Key**
  - `id`

- **Foreign Keys**
  - `district_id` → `berlin_source_data.districts(district_id)`

- **Checks**
  - `star_rating` must be between 1 and 5 if not NULL

- **Referential Action**
  -     ON DELETE RESTRICT
        ON UPDATE CASCADE

> Note: `neighborhood_id` is validated at query level.  
> A database-level foreign key is not enforced due to missing uniqueness
> constraints in the neighborhoods table.

---

## Data Sources

- **Primary:** OpenStreetMap (hotel entities)
- **Secondary:** Wikidata (star rating enrichment)
- **Geographic context:** Berlin administrative boundaries

---

## Load & Update Strategy

- Loaded via `hotels/scripts/hotels_transformation.ipynb`
- One-time batch insert into development database
- No automated refresh scheduled yet
- Intended for downstream consumption by analytics and recommender layers

---

## Validation

The following checks are applied during load:
- Row count verification
- Primary key uniqueness
- District foreign key validation
- Star rating value constraints
