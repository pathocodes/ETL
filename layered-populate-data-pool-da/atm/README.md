# atms — Layered DB Table Info

## Table Overview

- **Schema:** `berlin_source_data`
- **Table:** `atms`
- **Environment:** Development
- **Description:**  
  Contains cleaned and normalized atm data for Berlin, enriched with district
  and neighborhood references, intended for downstream analytics and applications.

Each row represents a single atm entity with geographic, descriptive,
and operational attributes.

---

## Columns

| Column name        | Type           | Nullable | Example value                         | Description |
|--------------------|----------------|----------|---------------------------------------|-------------|
| id                 | VARCHAR(20)    | No       | `86001840`                            | Unique atm identifier |
| district_id        | VARCHAR(20)    | No       | `11001001`                            | Foreign key reference to districts |
| neighborhood_id    | VARCHAR(20)    | Yes      | `0101`                                | Logical reference to neighborhoods |
| name               | VARCHAR(200)   | No       | `Berliner Volksbank`                       | operator name |
| latitude           | DECIMAL(9,6)   | Yes      | `52.512103`                           | Latitude coordinate |
| longitude          | DECIMAL(9,6)   | Yes      | `13.392540`                           | Longitude coordinate |
| geometry           | VARCHAR        | Yes      | `POINT (13.3925395 52.5121031)`       | WKT point representation |
| neighborhood       | VARCHAR(100)   | Yes      | `Mitte`                               | Neighborhood name |
| district           | VARCHAR(100)   | Yes      | `Mitte`                               | District name |
| address           | VARCHAR(200)   | Yes      | `Storkower Bogen, 10369, Berlin`                               | address |
| accessiblity           | VARCHAR(100)   | Yes      | `accessible`                               | accessible |
| atm_type           | VARCHAR(100)   | Yes      | `standalone`                               | atm_type |
| fee           | VARCHAR(100)   | Yes      | `free`                               | fee |
| opening_hours          | VARCHAR(100)   | Yes      | `24/7`                               | opening_hours    |



---

## Keys & Constraints

- **Primary Key**
  - `id`

- **Foreign Keys**
  - `district_id` → `berlin_source_data.districts(district_id)`

- **Referential Action**
  -     ON DELETE RESTRICT
        ON UPDATE CASCADE

> Note: `neighborhood_id` is validated at query level.  
> A database-level foreign key is not enforced due to missing uniqueness
> constraints in the neighborhoods table.

---

## Data Sources

- **Primary:** OpenStreetMap (atm entities)

---

## Load & Update Strategy

- Loaded via `atm/scripts/atms_to_database.ipynb
-- One-time batch insert into development database
- No automated refresh scheduled yet
- Intended for downstream consumption by analytics and recommender layers

---

## Validation

The following checks are applied during load:
- Row count verification
- Primary key uniqueness
- District foreign key validation
