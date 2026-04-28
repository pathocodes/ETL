# Dental Offices in Berlin – Data Collection & Analysis

## Overview
This project collects, processes, and analyzes data about dental practices in Berlin.
The focus lies on building a **lightweight, reproducible data pipeline** using openly available geospatial data.

The primary goal is to obtain a **consistent, enriched, and quality-checked dataset** of dental offices that can be used for:
- spatial analysis
- mapping and visualization
- comparison with other public health datasets
- downstream database ingestion or analytics workflows
---

## Project Structure

This project is organized to clearly separate raw data sources, processing logic, and cached artifacts generated during data preparation.

```text
project/
├── scripts/
│   ├── cache/
│   │   └── nominatim_reverse_cache.pkl
│   ├── dental_offices_data_prepocessing.ipynb
│   └── nominatim_reverse_cache.pkl
│
├── sources/
│   ├── Readme.md
│   ├── doctors_202601211553.csv
│   ├── raw_osm_dental_offices_v_01_19_2026.csv
│   └── raw_osm_dental_offices_v_01_19_2026.geojson
│
└── Readme.md
```

### **Directory Overview**
- `scripts/`
  Contains all data processing logic and intermediate artifacts.
    - `dental_offices_data_prepocessing.ipynb` -> Main notebook responsible for cleaning, normalizing, enriching, and validating dental office data.

- `cache/`
  Stores cached lookup results to avoid redundant external API calls.
    - `nominatim_reverse_cache.pkl` -> Cached reverse geocoding results (Nominatim) used to improve performance and reproducibility.

- `sources/`
  Holds all raw and reference data used as inputs for the processing pipeline.
    - `doctors_202601211553.csv` -> Reference dataset containing doctor-related records used to detect and
    remove overlapping identifiers from the dental offices dataset.
    - `raw_osm_dental_offices_v_01_19_2026.csv` -> Raw OpenStreetMap dental office data in tabular format.
    - `raw_osm_dental_offices_v_01_19_2026.geojson` -> Raw OpenStreetMap dental office data including geospatial features.
    - `Readme.md` -> Source-specific documentation describing data provenance and format details.

- `Readme.md`
  Main project documentation providing an overview of the project goals, data sources, and processing steps.


## Data Sources
### Evaluated Sources

The following data sources were evaluated:

 - OpenStreetMap (amenity=dentist)
 - Berlin Open Data Portal (health and medical facility datasets)
 - KZV Berlin (Kassenzahnärztliche Vereinigung – official registry)

After evaluation, **OpenStreetMap (OSM)** was selected as the primary data source.

OSM is the only source that provides **continuously updated, dynamic data** that can be accessed programmatically with minimal technical overhead. Data can be retrieved via standard APIs or extracts without requiring browser automation or additional infrastructure such as Selenium or WebDriver.

Other sources, while valuable for validation and legal verification, are either static, updated infrequently, or require complex scraping setups that are outside the scope of this project.

### OpenStreetMap (OSM)

| Field            | Description                                                                                                     |
|------------------|-----------------------------------------------------------------------------|
| source           | [OpenStreetMap (OSM) - API](https://overpass-api.de/api/interpreter), global crowdsourced geo DB                |
| update_frequency | Monthly / as published                                                                                          |
| data_type        | Dynamic (crowdsourced data accessed via API)                                                                    |
| relevant_fields | name, addr:street, addr:housenumber, addr:postcode, addr:city,<br>level, addr:floor, description, opening_hours,<br>check_date:opening_hours, check_date,<br>healthcare:speciality,<br>wheelchair, wheelchair:description, toilets:wheelchair,<br>phone, contact:website, contact:email, contact:phone, email, url, website,<br>geometry, health_facility:type,<br>health_specialty:oral_surgery, health_specialty:orthodontics, health_specialty:periodontology |
| license          | ODbL 1.0 (Open Database License); attribution required, share-alike applies |



## **Data Processing – Part 1: Integration & Normalization**

### 1.1. Data Extraction

Dental offices are fetched from OpenStreetMap using osmnx with the tag `amenity=dentist` for the geographic boundary of Berlin, Germany.

Both **CSV** and **GeoJSON** snapshots of the raw data are persisted to ensure full reproducibility and offline inspection.

### 1.2. Column Selection & Standardization

Only fields relevant to dental practices, accessibility, contact information, and geospatial analysis are retained.

OSM-style address tags are normalized into standardized column names (e.g. `addr:street` → `street`).

### 1.3. Speciality Mapping

Dental specialities are derived using a priority-based approach:
 - Use `healthcare:speciality` if populated
 - Otherwise infer speciality from boolean specialty flags (`oral_surgery`, `orthodontics`, `periodontology`)
 - Default to `None` if no information is available

Redundant raw specialty columns are dropped after consolidation.

### 1.4. Geometry Normalization

All geometries are converted to `point geometries`.
For non-point OSM features (e.g. polygons), representative points are used.

Latitude and longitude are extracted explicitly to support non-GIS workflows and database storage.

### 1.5. Attribute Consolidation

Multiple overlapping OSM attributes are merged into unified fields:

 - Phone numbers (`phone`, `contact:phone`)
 - Email addresses (`email`, `contact:email`)
 - Websites (`website`, `contact:website`, `url`)
 - Accessibility information (wheelchair access, toilets)
 - Check dates (general vs opening hours)

Custom merge logic ensures semantic clarity and avoids data loss.

### 1.6. Neighborhood & District Assignment

Each dental office is spatially joined with Berlin neighborhood (LOR Ortsteile) polygons.

The dataset is enriched with:

 - district
 - neighborhood
 - neighborhood identifier
 - standardized Berlin district IDs

Unmapped districts are explicitly reported for quality control.

### 1.7. Identifier Handling & Integrity Checks

OSM identifiers are preserved and normalized as string-based IDs to ensure database compatibility.

Basic integrity checks verify:

 - total record count
 - uniqueness of identifiers

### 1.8. Floor / Level Standardization

Floor information is standardized using locale-specific mappings (DE / UK / US supported), converting numeric or coded levels into human-readable formats (e.g. `0` → `EG`, `1` → `1.OG`).

### 1.9. Address Enrichment via Reverse Geocoding

Missing address components are enriched using **Nominatim reverse geocoding**.

**Key characteristics:**

 - strict rate limiting (1 request/second)
 - retry logic with spatial coordinate shifts
 - persistent local caching to minimize API usage
 - fallback handling for incomplete address responses

This step significantly improves address completeness while respecting public API usage policies.

### 1.10. Address Formatting

A standardized, human-readable address string is constructed from:

 - street
 - house number
 - floor
 - postal code
 - city
 - neighborhood

Only records with at least one valid address component are formatted.

### 1.11.  Data Quality Overview

The first processing stage concludes with:

 - column and datatype inspection
 - missing value analysis  
 - summary statistics for dataset size and completeness

This provides a clear baseline for subsequent processing steps.

### Licensing Notes

 - **OpenStreetMap data** is licensed under the **Open Database License (ODbL 1.0)**
  - Attribution to OpenStreetMap contributors is required
- Derived datasets must comply with share-alike provisions



## **Data Processing – Part 2: Deduplication, Cleaning & Validation**

This second processing stage focuses on **record deduplication, data cleaning, standardization, and final quality validation**.
Its goal is to ensure that each dental office is represented **exactly once**
and that the resulting dataset is **internally consistent, analysis-ready, and safe for downstream storage**.

### 2.1 Dental Office Deduplication Pipeline

OpenStreetMap data may contain multiple representations of the same dental office (e.g. nodes and polygons, duplicated entries, or slightly differing geometries). To address this, a **multi-stage deduplication strategy** is applied.

#### **Deduplication Strategy**

The pipeline removes duplicates using **three complementary criteria:**

**1. Normalized Name + Address**

 - Text normalization (lowercase, punctuation removal, standardized street forms)
 - Groups records that clearly refer to the same location

**2. Rounded Coordinates (~1 m precision)**

 - Geometry-based deduplication using rounded longitude/latitude
 - Collapses records with nearly identical point locations

**3. Centroid Proximity (~10 m) + Name Match**

 - Spatial clustering using a small distance threshold
 - Final safety net for near-duplicate geometries with identical names

Each stage progressively reduces duplicates while minimizing the risk of false merges.


#### **Duplicate Merging Logic**

When duplicates are detected, records are merged using a **safe merge strategy:**

 - Non-null values are preserved
 - Conflicting attributes are resolved conservatively
 - Latitude and longitude are averaged when multiple valid values exist
 - Geometry validity is maintained at all times

This ensures **maximum information retention** without introducing inconsistencies.


#### **Diagnostic Reporting**

For transparency and debugging, the pipeline generates **duplicate reports:**

 - Name + address duplicate counts
 - Cluster-based reports for centroid proximity matches

These reports allow manual inspection and validation of deduplication behavior.


### 2.2 Exclusion of Entries Present in Doctors Dataset

To prevent overlap between datasets, dental offices that already exist in the reference **doctors dataset** are explicitly removed.

**Procedure**

 - Load `doctors_202601211553.csv`
 - Identify overlapping identifiers (`id`)
 - Remove overlapping dental office records from the working dataset

This step guarantees **dataset separation** and avoids double-counting entities across different healthcare data sources.

### 2.3 Data Cleaning & Standardization Pipeline

After deduplication, all remaining records undergo systematic normalization.

#### **Column Name Standardization**

All column names are converted to **snake_case**:

 - lowercase
 - whitespace normalized
 - special characters removed

This improves consistency and database compatibility.


#### **Speciality Normalization**

Dental specialities are normalized using the following rules:

 - lowercase conversion
 - separator unification
 - splitting of multi-valued entries
 - deduplication and alphabetical ordering
 - re-joined using a pipe (`|`) delimiter

This enables **reliable filtering and aggregation** in downstream analyses.


#### **Generic String Normalization**

Selected text fields (`accessibility`, `description`, `check_date`) are normalized by:

 - trimming whitespace
 - converting to lowercase
 - preserving missing values as `None`

Phone numbers are cleaned to retain only digits and leading plus signs.


#### **Final Schema Selection**

The dataset is reduced to a **stable, analysis-ready schema**, including:

 - identifiers
 - address and contact information
 - accessibility and speciality metadata
 - geospatial attributes
 - administrative boundaries (district, neighborhood)


### 2.4 Missing Value Validation & Default Imputation

To ensure predictable behavior in analytics and databases, missing values
are handled explicitly.

#### **Validation**

 - Required columns are checked for existence
 - Missing critical columns raise hard errors

#### **Imputation Rules**

 - Fields with meaningful defaults (e.g. `name`) are filled
 - Optional fields are converted to explicit `None` (SQL NULL semantics)

A final missing-value report highlights any remaining gaps.

### 2.5 Final GeoDataFrame Quality Checks

The pipeline concludes with strict quality assertions:

 - All geometries are valid
 - Coordinate reference system is **WGS84 (EPSG:4326)**
 - No missing dental office names
 - All coordinates fall within Berlin’s geographic bounds

These checks ensure the dataset is:

 - spatially correct
 - internally consistent
 - safe for visualization, spatial joins, and database ingestion


#### **Resulting Dataset**

After completing Part 2, the project produces a **fully deduplicated, cleaned, and validated GeoDataFrame** of dental offices in Berlin.

The dataset is suitable for:

 - spatial analysis
 - mapping applications
 - integration into analytical databases
 - comparison with external healthcare datasets
  

## **Data Processing – Part 3: Production Load & Database Integration**
This final processing stage focuses on **persisting the validated dataset into a relational database**, enforcing **schema integrity**, and performing **post-load quality verification**.

The objective of Part 3 is to ensure that the dental offices dataset is:
- structurally stable  
- referentially consistent  
- safe for long-term analytical and operational use  

---

## 3. Production Load: Dental Offices Data Layer

### 3.1 Database Setup & Secure Connection

The pipeline establishes a secure connection to a PostgreSQL database using environment variables loaded from a `.env` file.

This approach ensures:
- separation of credentials from code  
- portability across environments (local, staging, production)  
- compatibility with CI/CD pipelines  

**Connection characteristics:**
- PostgreSQL via `psycopg2`
- SQLAlchemy engine abstraction
- SSL enforced where required

Environment variables define:
- database credentials
- schema names
- target table names
- reference tables for foreign key validation

Successful engine creation confirms database availability before proceeding.

---

### 3.2 Temporary Test Table (Validation & Debugging Layer)

Before writing to the production table, the dataset is loaded into a **temporary test table**.

This table serves as a **controlled validation environment** to verify:
- schema correctness  
- constraint enforcement  
- foreign key integrity  
- data type compatibility  

#### 3.2.1 Test Table Design

The test table mirrors the structure of the final production table and includes:

- primary key constraints  
- foreign key references to `DISTRICT_TABLE`  (real name is in .env = f'{DB_SCHEMA}.districts')
- geographic boundary checks for Berlin  
- domain-specific attributes (address, contact, accessibility, speciality)  

This design ensures that **any structural or referential issues are detected early**.

---

#### 3.2.2 Data Insertion & Validation

The cleaned and deduplicated dataset is bulk inserted using `pandas.to_sql`, allowing fast, transactional loading.

After insertion, the following checks are performed:

- verification that foreign key constraints exist  
- detection of orphan `district_id` values  
- explicit enforcement tests using invalid inserts  
- final row count comparison against the source DataFrame  

Only if **all test table checks pass successfully** does the pipeline proceed to the production table.

---

### 3.3 Final Production Table: `dental_offices`

The `dental_offices` table represents the **authoritative, normalized, and production-ready data layer** for dental offices in Berlin.

It is populated **only after** all upstream validation steps succeed.

---

#### 3.3.1 Purpose of the Final Table

The final table is designed to support:

- spatial analytics  
- public health analysis  
- mapping applications  
- integration with analytical warehouses  
- downstream services and APIs  

It guarantees:
- one row per dental office  
- enforced administrative consistency  
- predictable schema behavior  

---

#### 3.3.2 Final Table Schema (Explicit Description)

**Table Name:**  
`<schema>.dental_offices`

| Column Name        | Category                  | Type / Format               | Description |
|--------------------|---------------------------|----------------------------|-------------|
| `id`               | Primary Key               | VARCHAR(20)                | Stable string-based identifier (OSM-derived or pipeline-generated) |
| `name`             | Domain-Specific           | VARCHAR(200)               | Name of the dental practice; defaults to 'Unknown' if missing |
| `address`          | Address / Contact         | VARCHAR(255)               | Fully formatted, human-readable address |
| `phone`            | Address / Contact         | VARCHAR(50)                | Normalized phone number |
| `email`            | Address / Contact         | VARCHAR(100)               | Contact email address |
| `website`          | Address / Contact         | VARCHAR(200)               | Practice website URL |
| `opening_hours`    | Domain-Specific           | VARCHAR(200)               | OSM-compatible opening hours format |
| `check_date`       | Metadata                  | VARCHAR(255)               | Last known verification date (OSM or inferred) |
| `accessibility`    | Domain-Specific           | VARCHAR(100)               | Wheelchair and accessibility metadata |
| `speciality`       | Domain-Specific           | VARCHAR(150)               | Normalized dental specialities (pipe-delimited) |
| `description`      | Domain-Specific           | VARCHAR(500)               | Optional descriptive text |
| `office_type`      | Domain-Specific           | VARCHAR(100)               | Practice classification (e.g. single practice, group practice) |
| `geometry`         | Spatial                   | VARCHAR                    | Serialized point geometry (WKT-compatible) |
| `latitude`         | Spatial                   | DECIMAL(9,6)               | Latitude coordinate (WGS84 / EPSG:4326) |
| `longitude`        | Spatial                   | DECIMAL(9,6)               | Longitude coordinate (WGS84 / EPSG:4326) |
| `district`         | Administrative / Spatial  | VARCHAR(100)               | Human-readable Berlin district name |
| `neighborhood`     | Administrative / Spatial  | VARCHAR(100)               | LOR Ortsteil name |
| `district_id`      | Administrative / Spatial  | VARCHAR(20)                | Foreign key referencing `berlin_source_data.districts(district_id)` |
| `neighborhood_id`  | Administrative / Spatial  | VARCHAR(20)                | Official LOR identifier |


---

#### 3.3.3 Constraints & Guarantees

The final table enforces:

- **Primary key uniqueness**
- **Foreign key integrity** via `district_id`
- **Geographic bounds checks** ensuring all points lie within Berlin
- **Non-null guarantees** for critical identity fields  

These constraints ensure that **invalid or inconsistent records cannot enter production**.

---

#### 3.3.4 Data Insertion (Final Table)

After successful validation in the test table, the dataset is inserted into the final table.

This step represents the **commit point** of the pipeline.

Once populated, the `dental_offices` table is considered:
- authoritative  
- stable  
- ready for consumption  

---

### 3.4 Post-Load Data Quality Checks (Production Table)

After loading, additional **analytical sanity checks** are executed directly on the production table.

These checks include:

#### 3.4.1 Address Distribution Analysis
- Counts distinct addresses per district  
- Detects unexpected clustering or sparsity  
- Highlights potential remaining anomalies  

#### 3.4.2 Foreign Key Integrity Validation
- Confirms FK constraint existence  
- Verifies absence of orphan records  
- Actively tests FK enforcement with invalid inserts  

#### 3.4.3 Final Row Count Verification
- Confirms that the number of inserted rows matches expectations  
- Acts as a final completeness check  

Successful completion of these steps confirms that the dataset is:
- relationally consistent  
- geographically valid  
- production-grade  

---

## Resulting Data Asset

After completing all three processing stages, the project produces a dataset that is:

- fully deduplicated  
- spatially enriched  
- quality-validated  
- relationally consistent  

The `dental_offices` table serves as the **single source of truth** for all downstream use cases.