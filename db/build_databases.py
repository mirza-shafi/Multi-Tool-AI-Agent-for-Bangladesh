"""Convert data/raw/*.csv into SQLite DBs with meaningful, correctly-typed columns.

Column names and types below were taken from the real HuggingFace dataset
schemas (not guessed), so downstream tools can trust them.
"""

import os
import sqlite3

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DB_DIR = os.path.dirname(__file__)

# Each entry: csv filename, sqlite db filename, table name, column rename map
# (original CSV header -> clean snake_case name), and the sqlite type for
# each new column.
DATASETS = [
    {
        "csv": "hospitals.csv",
        "db": "hospitals.db",
        "table": "hospitals",
        "rename": {
            "Id": "id",
            "Name": "name",
            "Name (Bangla)": "name_bangla",
            "Code": "code",
            "Agency": "agency",
            "Type": "facility_type",
            "Division": "division",
            "District": "district",
            "City Corporation": "city_corporation",
            "Upazila": "upazila",
            "Paurasava": "paurasava",
            "Union": "union_name",
            "Private": "is_private",
        },
        "types": {
            "id": "INTEGER",
            "name": "TEXT",
            "name_bangla": "TEXT",
            "code": "INTEGER",
            "agency": "TEXT",
            "facility_type": "TEXT",
            "division": "TEXT",
            "district": "TEXT",
            "city_corporation": "TEXT",
            "upazila": "TEXT",
            "paurasava": "TEXT",
            "union_name": "TEXT",
            "is_private": "INTEGER",
        },
    },
    {
        "csv": "institutions.csv",
        "db": "institutions.db",
        "table": "institutions",
        "rename": {
            "INSTITUTE NAME": "institute_name",
            "EIIN": "eiin",
            "INSTITUTE_TYPE": "institute_type",
            "DIVISION_ID": "division_id",
            "DIVISION": "division",
            "DISTRICT_ID": "district_id",
            "DISTRICT": "district",
            "THANA_ID": "thana_id",
            "THANA": "thana",
            "UNION_ID": "union_id",
            "UNION_NAME": "union_name",
            "MAUZA_ID": "mauza_id",
            "MAUZA_NAME": "mauza_name",
            "AREA_STATUS": "area_status",
            "GEOGRPYCAL_STATUS": "geographical_status",
            "ADDRESS": "address",
            "POST": "post",
            "MANAGEMENT_TYPE": "management_type",
            "MOBILE": "mobile",
            "STUDENT_TYPE": "student_type",
            "EDUCATION_LEVEL": "education_level",
            "AFFILIATION": "affiliation",
            "MPO_STATUS": "mpo_status",
        },
        "types": {
            "institute_name": "TEXT",
            "eiin": "INTEGER",
            "institute_type": "TEXT",
            "division_id": "INTEGER",
            "division": "TEXT",
            "district_id": "INTEGER",
            "district": "TEXT",
            "thana_id": "INTEGER",
            "thana": "TEXT",
            "union_id": "INTEGER",
            "union_name": "TEXT",
            "mauza_id": "INTEGER",
            "mauza_name": "TEXT",
            "area_status": "TEXT",
            "geographical_status": "TEXT",
            "address": "TEXT",
            "post": "TEXT",
            "management_type": "TEXT",
            "mobile": "TEXT",
            "student_type": "TEXT",
            "education_level": "TEXT",
            "affiliation": "TEXT",
            "mpo_status": "TEXT",
        },
    },
    {
        "csv": "restaurants.csv",
        "db": "restaurants.db",
        "table": "restaurants",
        "rename": {
            "place_id": "place_id",
            "name": "name",
            "latitude": "latitude",
            "longitude": "longitude",
            "rating": "rating",
            "number_of_reviews": "number_of_reviews",
            "affluence": "affluence",
            "address": "address",
        },
        "types": {
            "place_id": "TEXT",
            "name": "TEXT",
            "latitude": "REAL",
            "longitude": "REAL",
            "rating": "REAL",
            "number_of_reviews": "INTEGER",
            "affluence": "REAL",
            "address": "TEXT",
        },
    },
]


def build_table(config):
    csv_path = os.path.join(RAW_DIR, config["csv"])
    db_path = os.path.join(DB_DIR, config["db"])

    df = pd.read_csv(csv_path)
    df = df.rename(columns=config["rename"])
    df = df[list(config["rename"].values())]

    for col, sql_type in config["types"].items():
        if sql_type == "INTEGER":
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        elif sql_type == "REAL":
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = df[col].astype("string")

    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(config["table"], conn, if_exists="replace", index=False, dtype=config["types"])
        conn.commit()
    finally:
        conn.close()

    print(f"{config['db']} -> table '{config['table']}' ({len(df)} rows, {len(df.columns)} columns)")


def main():
    for config in DATASETS:
        build_table(config)


if __name__ == "__main__":
    main()
