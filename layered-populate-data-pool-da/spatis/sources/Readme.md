# 🏪 Spätis — Data Source & Transformation Logic

## Primary Source

Spätis are sourced exclusively from **OpenStreetMap** via the Overpass API.

Query filters:

- `shop=convenience`
- `shop=kiosk`

The OSM extraction logic was reviewed and confirmed as correct and complete.

---

## Transformation Overview

Step 2 (Logic Refinement & Execution) was implemented to align the Spätis dataset with the standardized POI schema and database contract.

Existing logic for:
- OSM extraction
- spatial joins
- district and neighborhood mapping

was retained and verified.

Refinements were applied where required to close schema and contract gaps.

## Applied Refinements

- Enforced final POI schema column set
- Normalized ID fields to numeric string (`VARCHAR(20)` compatible)
- Renamed final ID column to `id` (schema-compliant)
- Applied conservative name normalization (casing + spelling variants)
- Ensured geometry is included and exported as WKT `POINT()` string
- Added final deduplication validation step (name + coordinates)
- Prepared POI-compliant final export dataset
- Created POI-schema compliant database table with required constraints
- The optional fields `beverage_emphasis` and `has_outdoor_area` were reviewed but not included.  
OSM does not provide reliable data for these attributes for Spätis, and default values would be misleading.

---

## Final POI Schema

The final dataset and database table follow the standardized POI schema:

| Column | Description |
|---------|-------------|
| `id` | OSM ID as numeric string, primary key |
| `district_id` | District identifier |
| `neighborhood_id` | neighborhood identifier |
| `name` | Store name (NOT NULL, default `Unknown`) |
| `latitude` | Latitude (numeric) |
| `longitude` | Longitude (numeric) |
| `geometry` | WKT `POINT(lon lat)` string |
| `district` | District name |
| `neighborhood` | Neighborhood name |
| `address` | Street name of the Späti location |
| `opening_hours` | Opening hours in free-text OSM format |

Foreign key constraint on `district_id`:
- `ON DELETE RESTRICT`
- `ON UPDATE CASCADE`

---

## Name Normalization

Name cleaning is applied conservatively to avoid semantic distortion:

- whitespace trimming
- consistent casing
- normalization of common spelling variants (e.g. Späti / Spätkauf)
- no merging or semantic renaming of individual stores

---

## ID Handling

Each record is derived from the OpenStreetMap object ID.

- validated as numeric-only
- converted to string
- limited to maximum length compatible with `VARCHAR(20)`
- exported as `id` to match POI schema

---

## Spatial Enrichment

Spätis are spatially joined with official Berlin LOR geometries to assign:

- `district_id`
- `neighborhood_id`
- `district`
- `neighborhood`

Coordinate reference systems are aligned before spatial joins to ensure spatial accuracy.

All coordinates are validated to fall within Berlin administrative boundaries.

---

## Deduplication Check

A final duplicate check was performed using:

- store name
- coordinates (proxy for ~10 m proximity)

Duplicates were removed.

---

## Hard-to-Clean Fields

address and opening_hours fields are kept as optional attributes. 
Coverage is low and formats vary, therefore no deep normalization was applied.

- address            824 non-null       
- opening_hours      714 non-null

---

## Address Enrichment (Nominatim)

Missing addresses were filled using reverse geocoding with OpenStreetMap Nominatim based on latitude and longitude.  
Requests use a custom user agent and a 1-second delay to respect API rate limits.  
If no street data was returned, the address remains null.
