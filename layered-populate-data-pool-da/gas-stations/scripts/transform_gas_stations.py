from pathlib import Path

import pandas as pd
import geopandas as gpd


# =====================================================
# OFFICIAL District mapping (Berlin) — 8-digit strings
# Reviewer-approved mapping
# =====================================================
DISTRICT_ID_BY_NAME = {
    "Mitte": "11001001",
    "Friedrichshain-Kreuzberg": "11002002",
    "Pankow": "11003003",
    "Charlottenburg-Wilmersdorf": "11004004",
    "Spandau": "11005005",
    "Steglitz-Zehlendorf": "11006006",
    "Tempelhof-Schöneberg": "11007007",
    "Neukölln": "11008008",
    "Treptow-Köpenick": "11009009",
    "Marzahn-Hellersdorf": "11010010",
    "Lichtenberg": "11011011",
    "Reinickendorf": "11012012",
}


# -----------------------
# Helpers
# -----------------------
def to_snake(s: str) -> str:
    return (
        str(s)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(":", "_")
    )


def normalize_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip()


def safe_point_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Ensure CRS is EPSG:4326 and geometries are Points.
    Convert non-Point geometries to representative points.
    """
    gdf = gdf.copy()

    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")

    is_point = gdf.geometry.geom_type == "Point"
    if (~is_point).any():
        gdf.loc[~is_point, "geometry"] = gdf.loc[~is_point, "geometry"].representative_point()

    return gdf


def find_lor_file(sources_dir: Path) -> Path:
    """
    Prefer sources/lor_ortsteile.geojson
    If not found, try sources/lor_ortsteile*.geojson
    """
    preferred = sources_dir / "lor_ortsteile.geojson"
    if preferred.exists():
        return preferred

    matches = sorted(sources_dir.glob("lor_ortsteile*.geojson"))
    if matches:
        return matches[0]

    raise FileNotFoundError(
        f"LOR file not found.\nExpected: {preferred}\nOr like: sources/lor_ortsteile (1).geojson"
    )


def load_lor(lor_path: Path) -> gpd.GeoDataFrame:
    """
    Load LOR Ortsteile polygons and normalize to:
      neighborhood, neighborhood_id, district, district_id, geometry

    Reviewer note:
      - neighborhood_id must come from spatial_alias (4-digit like 0105)
      - district can be pulled directly from BEZIRK
      - district_id comes from mapping
    """
    lor = gpd.read_file(lor_path)

    # CRS normalization
    if lor.crs is None:
        lor = lor.set_crs("EPSG:4326")
    else:
        lor = lor.to_crs("EPSG:4326")

    geom_col = lor.geometry.name

    # Upper-case non-geometry columns for robust matching
    lor = lor.rename(columns={c: c.upper() for c in lor.columns if c != geom_col})
    cols = set(lor.columns)

    if {"SPATIAL_NAME", "SPATIAL_ALIAS", "BEZIRK"}.issubset(cols):
        gdf_lor_small = lor[["SPATIAL_NAME", "SPATIAL_ALIAS", "BEZIRK", geom_col]].copy()
        gdf_lor_small = gdf_lor_small.rename(
            columns={
                "SPATIAL_NAME": "neighborhood",
                "SPATIAL_ALIAS": "neighborhood_id",
                "BEZIRK": "district",
                geom_col: "geometry",
            }
        )
    else:
        raise ValueError(
            "LOR file does not contain expected columns.\n"
            f"Found: {lor.columns.tolist()}\n"
            "Expected: SPATIAL_NAME, SPATIAL_ALIAS, BEZIRK"
        )

    gdf_lor_small = gdf_lor_small.set_geometry("geometry")

    # Clean types (DO NOT fill nulls; only standardize)
    gdf_lor_small["neighborhood"] = gdf_lor_small["neighborhood"].astype("string").str.strip()
    gdf_lor_small["neighborhood_id"] = (
        gdf_lor_small["neighborhood_id"].astype("string").str.strip().str.zfill(4)
    )
    gdf_lor_small["district"] = gdf_lor_small["district"].astype("string").str.strip()

    # district_id from district (official codes)
    gdf_lor_small["district_id"] = gdf_lor_small["district"].map(DISTRICT_ID_BY_NAME).astype("string")

    # Keep only needed cols
    return gdf_lor_small[["district", "district_id", "neighborhood", "neighborhood_id", "geometry"]].copy()


def build_address_from_osm(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Build address from OSM-style fields.
    IMPORTANT: keep null if parts missing (do NOT force 'unknown').

    Output format:
      "<street> <housenumber>, <postcode> <city>"
    """
    gdf = gdf.copy()

    def clean_part(col: str) -> pd.Series:
        if col not in gdf.columns:
            return pd.Series([pd.NA] * len(gdf), dtype="string")
        s = gdf[col].astype("string").str.strip()
        s = s.replace("", pd.NA)
        return s

    street = clean_part("addr_street")
    hn = clean_part("addr_housenumber")
    pc = clean_part("addr_postcode")
    city = clean_part("addr_city")

    line1 = (street.fillna("") + " " + hn.fillna("")).str.strip().replace("", pd.NA)
    line2 = (pc.fillna("") + " " + city.fillna("")).str.strip().replace("", pd.NA)

    address = pd.Series([pd.NA] * len(gdf), dtype="string")
    has1 = line1.notna()
    has2 = line2.notna()

    address[has1 & has2] = (line1[has1 & has2] + ", " + line2[has1 & has2]).astype("string")
    address[has1 & ~has2] = line1[has1 & ~has2].astype("string")
    address[~has1 & has2] = line2[~has1 & has2].astype("string")

    gdf["address"] = address
    return gdf


def export_safe(gdf_final: gpd.GeoDataFrame, out_csv: Path, out_geojson: Path) -> int:
    """
    Export only schema-safe columns to avoid GeoJSON export errors
    from dict/list/object columns.
    """
    EXPORT_COLS = [
        "id",
        "name",
        "brand",
        "operator",
        "address",
        "latitude",
        "longitude",
        "district",
        "district_id",
        "neighborhood",
        "neighborhood_id",
        "opening_hours",
        "car_wash",
        "compressed_air",
        "wheelchair",
        "fuel:diesel",
        "fuel:octane_95",
        "fuel:electricity",
        "geometry",
    ]
    EXPORT_COLS = [c for c in EXPORT_COLS if c in gdf_final.columns]
    gdf_export = gdf_final[EXPORT_COLS].copy()

    # CSV: store geometry as WKT (so CSV stays usable)
    df_csv = pd.DataFrame(gdf_export.drop(columns=["geometry"], errors="ignore")).copy()
    if "geometry" in gdf_export.columns:
        df_csv["geometry_wkt"] = gdf_export.geometry.to_wkt()
    df_csv.to_csv(out_csv, index=False)

    # GeoJSON: keep geometry
    gdf_export.to_file(out_geojson, driver="GeoJSON")

    return len(gdf_export)


def main() -> None:
    # -----------------------
    # Paths
    # -----------------------
    base_dir = Path(__file__).resolve().parents[1]  # .../gas-stations
    sources_dir = base_dir / "sources"

    raw_geojson = sources_dir / "gas_stations_raw.geojson"
    out_csv = sources_dir / "gas_stations_transformed.csv"
    out_geojson = sources_dir / "gas_stations_transformed.geojson"

    if not raw_geojson.exists():
        raise FileNotFoundError(f"Raw file not found: {raw_geojson}")

    # -----------------------
    # Load raw gas stations
    # -----------------------
    gdf = gpd.read_file(raw_geojson)
    gdf = safe_point_geometry(gdf)

    # Standardize column names
    gdf.columns = [to_snake(c) for c in gdf.columns]

    # Ensure required "name" exists and ONLY fill name
    if "name" not in gdf.columns and "station_name" in gdf.columns:
        gdf = gdf.rename(columns={"station_name": "name"})
    if "name" not in gdf.columns:
        gdf["name"] = pd.NA

    gdf["name"] = normalize_text(gdf["name"]).fillna("")
    gdf.loc[gdf["name"] == "", "name"] = "unknown gas station"
    gdf.loc[gdf["name"].isin(["unknown", "Unknown"]), "name"] = "unknown gas station"

    # lat/lon
    gdf["longitude"] = gdf.geometry.x
    gdf["latitude"] = gdf.geometry.y

    # address (keep nulls)
    gdf = build_address_from_osm(gdf)

    # -----------------------
    # Load LOR + spatial join
    # -----------------------
    lor_path = find_lor_file(sources_dir)
    lor = load_lor(lor_path)

    if gdf.crs != lor.crs:
        gdf = gdf.to_crs(lor.crs)

    gdf = gpd.sjoin(gdf, lor, how="left", predicate="within").drop(columns=["index_right"], errors="ignore")

    # Ensure neighborhood_id is 4-digit
    if "neighborhood_id" in gdf.columns:
        gdf["neighborhood_id"] = gdf["neighborhood_id"].astype("string").str.zfill(4)

    # If district exists but district_id missing (safety net)
    if "district" in gdf.columns and "district_id" not in gdf.columns:
        gdf["district_id"] = gdf["district"].map(DISTRICT_ID_BY_NAME).astype("string")

    # -----------------------
    # Deduplicate (reviewer-safe)
    # Use id when present; fallback to name+coords
    # -----------------------
    if "id" in gdf.columns:
        gdf_final = gdf.drop_duplicates(subset=["id"]).copy()
    else:
        gdf["lat_round"] = gdf["latitude"].round(6)
        gdf["lon_round"] = gdf["longitude"].round(6)
        gdf_final = gdf.drop_duplicates(subset=["name", "lat_round", "lon_round"]).copy()
        gdf_final = gdf_final.drop(columns=["lat_round", "lon_round"], errors="ignore")

    # -----------------------
    # QA checks (reviewer)
    # -----------------------
    assert gdf_final["name"].isna().sum() == 0, "Name still has nulls (should be 'unknown gas station')."
    assert (gdf_final["name"] == "unknown").sum() == 0, "Found 'unknown' (should be 'unknown gas station')."
    assert "district_id" in gdf_final.columns, "district_id column missing."

    # Optional: quick mapping preview
    if "district" in gdf_final.columns and "district_id" in gdf_final.columns:
        preview = gdf_final[["district", "district_id"]].drop_duplicates().sort_values("district_id")
        print(preview.to_string(index=False))

    # -----------------------
    # Export (FINAL dataframe = gdf_final)
    # -----------------------
    n_rows = export_safe(gdf_final, out_csv, out_geojson)
    print(f"✅ Saved {n_rows} rows to:\n- {out_csv}\n- {out_geojson}")


if __name__ == "__main__":
    main()