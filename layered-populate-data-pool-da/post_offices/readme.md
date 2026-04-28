## **Data Modeling: Berlin Postal Services**
---
**1. Data Cleaning & Brand Normalization**

The raw OpenStreetMap (OSM) data contained inconsistent naming conventions. 
I implemented a keyword-based mapping logic to unify these into clean categories:
- Deutsche Post: Consolidated variations like Postbank, Postfiliale, and Deutsche Post AG.
- Amazon: Identified and grouped Amazon Hub Locker and Amazon Locker.
- DHL: Unified Packstation, Paketbox, and DHL Express.
- Kiosk: Grouped independent postal agents such as Späti, Lotto, and Kiosk.
- Else: Independent Retailer

**2. Feature Extraction (Regex)**

Many branch IDs and locker numbers were embedded within the name string. I used Regular Expressions (r'\d{3,}') to:
- Extract sequences of 3 or more digits from the name column.
- Populate the ref column if the original OSM ref was missing (NaN).
- Ensure that branch identifiers are structured and searchable.

**3. Data Refinement & Schema Alignment**

To ensure the dataset is production-ready, I performed the following operations:

- Deduplication: Removed duplicate entries based on osm_id.
- Centroid Extraction: Calculated the center point for polygon-based geometries to ensure every POI has a precise latitude and longitude.
- Column Pruning: Removed redundant raw tags (original name) using an error-proof List Comprehension method.
- Reordering: Standardized the column order: id → name → ref → latitude → longitude → geometry.

## **Data Transformation: Berlin Postal Services**
---
**1. Normalize and Renaming Columns**
- Standardized 'operator' names and 'street' columns for consistency.

**2. Geopandas (Spatial Join)**
- Merged postal data with lor_ortsteile.geojson to automatically assign Bezirk (District) and Neighborhood to each location.

**3. Spatial Deduplication**
- Grouped data by operator and merged points within a 50m radius.
- Calculated Centroids for overlapping points and consolidated service attributes (merging "yes" values).
- Used cKDTree for high-efficiency neighbor searching.

**4. Reverse Geocoding**
- Used geopy (Nominatim) to fill missing addresses (NaN) based on existing coordinates.
- Implemented Rate Limiting (1 request/second) and Timeouts to ensure stable and ethical data retrieval from OpenStreetMap.

## **Production Load (ETL)**
---
**1. Extraction and Driver Compatibility**
Data was pushed to a PostgreSQL database (hosted on Neon.tech) using SQLAlchemy and the psycopg driver.

**2. WKT Conversion**
Shapely Geometry objects were converted into WKT (Well-Known Text) strings. This architectural choice facilitates seamless data exchange between systems that may not have full PostGIS extensions implemented, while maintaining high coordinate precision.

**3. Schema Enforcement**
**Table:** berlin_source_data.post_offices_final_hana

* **id** (BIGINT): Unique OpenStreetMap Identifier. PRIMARY KEY.
* **district_id** (VARCHAR): Link to Berlin district master table. FOREIGN KEY, NOT NULL.
* **amenity** (VARCHAR): Facility type (post_office/parcel_locker). NOT NULL.
* **operator** (VARCHAR): Normalized operator or brand name. NOT NULL.
* **addr_street** (VARCHAR): Street name of the facility. NOT NULL.
* **geometry** (VARCHAR): Spatial coordinates in WKT format. NOT NULL.
* **latitude** (DECIMAL 9,6): Geographic Latitude. CHECK (Berlin Bounds).
* **longitude** (DECIMAL 9,6): Geographic Longitude. CHECK (Berlin Bounds).

---

## Quality Assurance (QA) and Validation Report

* **Row Count Integrity:** 950 / 950 rows (Matches Python DataFrame). Status: Passed.
* **Foreign Key Check:** 0 orphan rows on district_id. Status: Passed.
* **Bounding Box Validation:** 0 Outliers (All coordinates within Berlin limits). Status: Passed.
* **Nullity Check:** 0 NULLs in mandatory columns (id, operator, district_id, amenity). Status: Passed.
* **Spatial Coverage:** Data successfully distributed across all 12 Districts. Status: Passed.

### Consistency Insights
* Major entities like Amazon show 100% consistency in known records, while DHL maintains a high alignment despite minor crowdsourced tagging anomalies.
* Minor tagging conflicts (e.g., DHL brand vs. Hermes operator) were identified in the source data but do not impact core functionality.
* The Pankow district contains the highest density of facilities (129 units).

---

## How to Run
1. Ensure your .env file contains a valid DATABASE_URL.
2. Run the production_load.ipynb notebook.
3. Verify the load using the following SQL query:

   SELECT district, COUNT(*) FROM berlin_source_data.post_offices_final_hana GROUP BY district;

---

### Technical Note
Coordinates are stored as WKT Strings within a VARCHAR column. This prevents driver errors and ensures data remains accessible even in environments without spatial extensions.
