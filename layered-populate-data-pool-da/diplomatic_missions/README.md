# Diplomatic missions — Layered DB Table Info

## Table Overview

- **Schema:** `berlin_source_data`
- **Table:** `diplomatic_missions`
- **Environment:** Development
- **Description:**  
  Contains cleaned and normalized data for diplomatic missions in Berlin. It provides a structured dataset of official foreign representations in Berlin, including embassies, consulates, honorary consulates, and nunciatures.
  
  It supports spatial analysis and neighborhood-level context for diplomatic presence within the city. Each row represents a single diplomatic mission with geographic, descriptive and operational attributes.

---

## Schema

### Core POI Fields

- `id`
- `district_id`
- `name`
- `latitude`
- `longitude`
- `geometry`
- `neighborhood`
- `district`
- `neighborhood_id`

### Mission-Specific Fields

- `mission_type`
- `country_iso_code`
- `address`
- `website`

---

## Columns

| Column Name        | Type        |  Nullable | Example value     | Description |
|--------------------|------------------|-------------|-------------|-------------|
| id                 | VARCHAR(20)      |  No       | `1880606692` | Unique identifier of the diplomatic mission (Primary Key) |
| district_id        | VARCHAR(20)      |  No       |  `11007007` | Identifier of the Berlin district (Foreign Key) |
| name               | VARCHAR(200)     |  No       |  `Botschaft Argentinien` | Official name of the diplomatic mission |
| latitude           | DECIMAL(9,6)     |  Yes       |  `52.501211` | Latitude coordinate of the mission location |
| longitude          | DECIMAL(9,6)     |  Yes       |  `13.344571` | Longitude coordinate of the mission location |
| geometry           | VARCHAR          |  Yes       |  `POINT(13.3445706 52.5012109)` | Geospatial representation (e.g., WKT format) |
| neighborhood       | VARCHAR(100)     |  Yes       | `Schöneberg`  | Name of the neighborhood |
| district           | VARCHAR(100)     |  Yes       |  `Tempelhof-Schöneberg` | Name of the district |
| neighborhood_id    | VARCHAR(20)      |  Yes       |  `0701` | Identifier of the neighborhood |
| country_iso_code   | CHAR(2)          |  Yes       | `AR`  | ISO 3166-1 alpha-2 country code (e.g., 'US', 'FR') |
| mission_type       | VARCHAR(50)      |  Yes       | `embassy`  | Type of mission (Embassy, Consulate, Honorary Consulate) |
| address            | VARCHAR(200)     |  Yes       |  `Kleiststraße 23-26, 10787 Berlin` | Street address |
| website            | VARCHAR(200)     |  Yes       |  `http://www.ealem.mrecic.gov.ar/` | Official website |
| email              | VARCHAR(100)     |  Yes       |  `None` | Contact email address |

---

## Keys & Constraints

- **Primary Key:** 
  - `id`

- **Foreign Key:** 

  - `district_id` → `berlin_source_data.districts(district_id)`

- **Referential Action**
  - `ON DELETE RESTRICT`
  - `ON UPDATE CASCADE`

---

## Data Sources

### Primary Source
- OpenStreetMap (OSM) – diplomatic offices (`office=embassy`, `diplomatic=*`)

### Evaluated but Not Integrated
- Wikidata  
- German Federal Foreign Office (Auswärtiges Amt)

Wikidata and the official Foreign Office list were reviewed and compared against OSM.  
Due to negligible overlap improvements and no critical missing attributes in the OSM dataset, a merge was not considered meaningful for the MVP.  
OSM therefore remains the sole integrated source.

---

## Load & Update Strategy

- Loaded via `diplomatic-missions/scripts/missions_transformation.ipynb`
- One-time batch insert into development database
- No automated refresh scheduled yet
- Intended for downstream consumption by analytics and recommender layers

---

## Validation

- Duplicate detection (name + spatial proximity)
- Country code consistency validation
- Mission-type normalization
- Spatial integrity validation
- Missing value assessment

Only verified technical duplicates were consolidated.  
Distinct diplomatic facilities located at different sites were retained.