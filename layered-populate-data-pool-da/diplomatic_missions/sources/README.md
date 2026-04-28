# 1.1 Data Source Discovery

- Main source: OpenStreetMap (OSM)
- Reason: Open, free, community-maintained, and continuously updated geospatial dataset with detailed tagging for diplomatic missions.
- Data type: Dynamic (can be refreshed automatically via API).
- Update frequency: Continuous (OSM data changes continuously; dataset snapshots can be generated on demand).

- Supplementary sources: Used only to fill gaps and for data validation, not as authoritative primary sources.
    - Wikidata
        - Purpose: Stable identifiers (Q-IDs), links, and cross-references.
        - License: CC0 (Public Domain).
    - Official government sources (e.g. Auswärtiges Amt, berlin.de)
        - Purpose: Verification of existence and official naming.
    - Private aggregators (e.g. EmbassyPages, Embassy-Berlin.net, CIBTvisas)
        - Purpose: Gap detection and contact detail hints.
        - Note: Not redistributed as primary data due to licensing constraints.

## OSM

Link: https://overpass-turbo.eu/ + Query

| Field | Description |
|------|-------------|
| source | OpenStreetMap via Overpass Turbo, Berlin administrative area |
| update_frequency | one-time export, constantly on the site |
| data_type | Static (one-time import) |
| license | ODbL 1.0 (Open Database License) – © OpenStreetMap contributors |

---

## Wikidata

Link: https://query.wikidata.org/ + query

| Field | Description |
|------|-------------|
| source | Wikidata (Wikidata Query Service / SPARQL), items located in Berlin |
| update_frequency | one-time export, Constantly updated on Wikidata |
| data_type | Static (one-time import) |
| license | CC0 1.0 (Public Domain) – provided by Wikidata contributors |

---

## berlin.de

Link: 

| Field | Description |
|------|-------------|
| source | Land Berlin – berlin.de (Tourismusportal: „Botschaften in Berlin“) |
| update_frequency | static |
| data_type | Static (one-time import) |
| license | © Land Berlin – Use in accordance with berlin.de terms of use |

---

## auswaertigesamt

Stand Okt 2025 aus pdf

https://www.auswaertiges-amt.de/de/reiseundsicherheit/vertretungen-anderer-staaten

| Field | Description |
|------|-------------|
| source | Auswärtiges Amt (Deutschland) – „Vertretungen anderer Staaten in Deutschland“ (PDF) |
| update_frequency | Irregular (maintained by the Auswärtiges Amt); snapshot export |
| data_type | Static (one-time import) |
| license | © Auswärtiges Amt – Use in accordance with auswaertiges-amt.de terms of use |

---

## Private pages
They serve at most for data verification or to fill in missing data.

---

### Embassy-Berlin.net

Link: https://embassy-berlin.net

| Field | Description |
|------|-------------|
| source | Embassy-Berlin.net (private, non-governmental website with address lists of diplomatic missions in Berlin) |
| update_frequency | static |
| data_type | Static (one-time import) |
| license | © Embassy-Berlin.net – Use in accordance with Embassy-Berlin.net terms of use |

---

### embassypages

Link: https://www.embassypages.com/stadt/berlin

| Field | Description |
|------|-------------|
| source | EmbassyPages (private, non-governmental website aggregating contact details of diplomatic missions worldwide) |
| update_frequency | Irregular (maintained by site operator); snapshot export |
| data_type | Static (one-time import) |
| license | © EmbassyPages – Use in accordance with embassypages.com terms of use |

---

# 1.2. Diplomatic Missions – Modelling & Preprocessing

## Overview

This data layer provides a structured dataset of official foreign representations in Berlin, including embassies, consulates, honorary consulates, and nunciatures.  
It supports spatial analysis and neighborhood-level context for diplomatic presence within the city.

The dataset was prepared as part of the **Data Transformation & Preprocessing (Step 2)** workflow.

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

## Data Processing

The following transformation steps were applied:

- Standardization of core schema fields  
  (`name`, `mission_type`, `sending_country`, `address`, `postal_code`, `latitude`, `longitude`, `geometry`, `contact_info`, `website`, `data_source`)
- CRS validation (EPSG:4326)
- Spatial enrichment using official Berlin district and neighborhood boundaries
- Manual validation of duplicate records
- Consolidation of technical OSM duplicates (e.g., node/way overlaps)
- Normalization of country identifiers (ISO-2 codes retained)

Non-essential metadata fields (e.g., accessibility or incomplete contact details) were not artificially completed in order to preserve source integrity.

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
- `sending_country`
- `address`
- `postal_code`
- `accessibility`
- `contact_info`
- `website`
- `data_source`

---

## Quality Assurance

Quality checks included:

- Duplicate detection (name + spatial proximity)
- Country code consistency validation
- Mission-type normalization
- Spatial integrity validation
- Missing value assessment

Only verified technical duplicates were consolidated.  
Distinct diplomatic facilities located at different sites were retained.
