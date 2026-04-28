# Social Clubs Data Layer - Audit Report

**Branch:** social-clubs-alignment-audit for Issue #616  
**Referenz:** Issue #592  
**Datum:** 2025-02-04  
**Tabelle:** `berlin_source_data.social_clubs_activities`

---

## Übersicht

| Metrik | Wert |
|--------|------|
| Total Records | 1.658 |
| Spalten | 22 |
| Geometry Type | POINT (100%) |

---

## 2. Missing Values

### Kritische Felder (0% Missing - OK)

- id
- name
- latitude
- longitude
- geometry
- district_id
- neighborhood_id
- district
- neighborhood
- full_address
- opening_hours
- wheelchair

### OSM Tag Felder (hohe Missing-Rate erwartet)

| Feld | Missing | Prozent |
|------|---------|---------|
| leisure | 1.596 | 96,3% |
| sport | 1.443 | 87,0% |
| club | 1.313 | 79,2% |
| amenity | 302 | 18,2% |

### Kontaktdaten

| Feld | Missing | Prozent |
|------|---------|---------|
| email | 1.485 | 89,6% |
| phone | 1.379 | 83,2% |
| website | 955 | 57,6% |
| postcode | 602 | 36,3% |
| housenumber | 563 | 34,0% |
| street | 553 | 33,4% |

### Placeholder-Werte

- opening_hours = 'unknown': 1.289
- wheelchair = 'unknown': 1.327

---

## 3. Data Validity

| Check | Ergebnis | Status |
|-------|----------|--------|
| Duplicate IDs | 0 | OK |
| Non-numeric IDs | 0 | OK |

### Kategorische Werte

**amenity:** events_venue, arts_centre, community_centre, social_centre, studio, dojo, music_school, dancing_school, music_venue, photo_booth, social_club

**wheelchair:** true, false, unknown

---

## 4. Geometry Validation

| Check | Ergebnis | Status |
|-------|----------|--------|
| Geometry Type | POINT | OK |
| Missing Geometries | 0 | OK |
| Outside Berlin | 0 | OK |

### Koordinaten-Bereich

| Dimension | Min | Max | Berlin Bounds |
|-----------|-----|-----|---------------|
| Latitude | 52.3739 | 52.6448 | 52.34 - 52.68 |
| Longitude | 13.1224 | 13.7311 | 13.09 - 13.76 |

---

## 5. District & Neighborhood IDs

### Verteilung nach Bezirk

| Bezirk | ID | Anzahl |
|--------|-----|--------|
| Mitte | 11001001 | 247 |
| Friedrichshain-Kreuzberg | 11002002 | 215 |
| Pankow | 11003003 | 177 |
| Treptow-Köpenick | 11009009 | 166 |
| Charlottenburg-Wilmersdorf | 11004004 | 152 |
| Neukölln | 11008008 | 138 |
| Tempelhof-Schöneberg | 11007007 | 132 |
| Steglitz-Zehlendorf | 11006006 | 103 |
| Lichtenberg | 11011011 | 95 |
| Reinickendorf | 11012012 | 91 |
| Spandau | 11005005 | 81 |
| Marzahn-Hellersdorf | 11010010 | 61 |

### Foreign Key Status

| Constraint | Column | References | Delete Rule |
|------------|--------|------------|-------------|
| district_id_fk | district_id | districts | RESTRICT |

Orphan district_ids: 0 (OK)

---

## 6. Schema Compliance

### Aktuelles Schema

| Column | Data Type | Max Length | Nullable |
|--------|-----------|------------|----------|
| id | VARCHAR | 100 | NO |
| name | VARCHAR | 200 | NO |
| club | VARCHAR | 100 | YES |
| leisure | VARCHAR | 100 | YES |
| sport | VARCHAR | 100 | YES |
| amenity | VARCHAR | 100 | YES |
| street | VARCHAR | 200 | YES |
| housenumber | VARCHAR | 50 | YES |
| postcode | VARCHAR | 20 | YES |
| website | VARCHAR | 250 | YES |
| phone | VARCHAR | 100 | YES |
| email | VARCHAR | 150 | YES |
| opening_hours | TEXT | - | YES |
| wheelchair | VARCHAR | 50 | YES |
| latitude | NUMERIC | - | NO |
| longitude | NUMERIC | - | NO |
| district | VARCHAR | 100 | YES |
| neighborhood_id | VARCHAR | 100 | YES |
| neighborhood | VARCHAR | 100 | YES |
| full_address | TEXT | - | YES |
| district_id | VARCHAR | 100 | NO |
| geometry | TEXT | - | YES |

### Compliance vs Issue #592

Schema entspricht den Anforderungen. Alle Required Columns vorhanden.

---

## 7. Zusammenfassung

### Bestanden

- Alle kritischen Felder vollständig (0% missing)
- Keine Duplikate bei Primary Key
- Alle IDs numerisch
- Alle Geometrien gültig (POINT)
- Alle Koordinaten innerhalb Berlin
- FK-Constraint vorhanden (ON DELETE RESTRICT)
- Keine Orphan district_ids
- Schema-Konformität mit Issue #592

### Hinweise

- **Placeholder-Werte:** opening_hours und wheelchair enthalten viele 'unknown' Werte (ca. 78-80%)
- **Kontaktdaten:** Hohe Missing-Rates bei email (90%), phone (83%), website (58%)
