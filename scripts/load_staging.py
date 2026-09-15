import os
import sys
from pathlib import Path

import pandas as pd
import pyodbc


BASE_DIR = Path.home() / "data-engineering-test"
RAW_DIR = BASE_DIR / "data" / "raw"


TABLE_CONFIG = {
    "customers": {
        "file": "customers.csv",
        "table": "staging.customers",
        "columns": [
            "customer_id",
            "name",
            "email",
            "city",
            "signup_date",
        ],
    },
    "products": {
        "file": "products.csv",
        "table": "staging.products",
        "columns": [
            "product_id",
            "product_name",
            "category",
            "price",
        ],
    },
    "transactions": {
        "file": "transactions.csv",
        "table": "staging.transactions",
        "columns": [
            "transaction_id",
            "customer_id",
            "transaction_date",
            "total_amount",
        ],
    },
    "transaction_items": {
        "file": "transaction_items.csv",
        "table": "staging.transaction_items",
        "columns": [
            "transaction_item_id",
            "transaction_id",
            "product_id",
            "quantity",
            "price",
        ],
    },
    "marketing_campaigns": {
        "file": "marketing_campaigns.csv",
        "table": "staging.marketing_campaigns",
        "columns": [
            "campaign_id",
            "campaign_name",
            "start_date",
            "end_date",
            "channel",
        ],
    },
}


#def get_connection():
#    connection_string = (
#        "DRIVER={ODBC Driver 18 for SQL Server};"
#        f"SERVER={os.environ['MSSQL_HOST']},{os.environ['MSSQL_PORT']};"
#        f"DATABASE={os.environ['MSSQL_DATABASE']};"
#        f"UID={os.environ['MSSQL_USERNAME']};"
#        f"PWD={os.environ['MSSQL_PASSWORD']};"
#        "TrustServerCertificate=yes;"
#    )
#
#    return pyodbc.connect(connection_string)
def get_connection():
    from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook

    hook = MsSqlHook(mssql_conn_id="mssql_tesde")
    return hook.get_conn()

def load_csv_to_staging(source_name):

    if source_name not in TABLE_CONFIG:
        raise ValueError(
            f"Unknown source: {source_name}. "
            f"Available: {list(TABLE_CONFIG.keys())}"
        )

    config = TABLE_CONFIG[source_name]

    csv_path = RAW_DIR / config["file"]
    table_name = config["table"]
    columns = config["columns"]

    print(f"Reading: {csv_path}")

    df = pd.read_csv(csv_path)

    print(f"Rows read: {len(df)}")
    print(f"Target table: {table_name}")

    df = df[columns]

    placeholders = ", ".join(["%s"] * len(columns))
    column_list = ", ".join(columns)

    sql = f"""
        INSERT INTO {table_name} ({column_list})
        VALUES ({placeholders})
    """

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {table_name}")

    rows = [
        tuple(None if pd.isna(value) else value for value in row)
        for row in df.itertuples(index=False, name=None)
    ]

    cursor.executemany(sql, rows)

    connection.commit()

    cursor.close()
    connection.close()

    print(
        f"Successfully loaded {len(rows)} rows "
        f"into {table_name}"
    )


if __name__ == "__main__":

    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python load_staging.py <source_name>"
        )

    load_csv_to_staging(sys.argv[1])
