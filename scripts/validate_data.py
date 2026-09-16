import os
import pyodbc


def get_connection():
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.getenv('DB_SERVER')},{os.getenv('DB_PORT', '1433')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(connection_string)

def run_validation():
    connection = get_connection()
    cursor = connection.cursor()

    errors = []

    try:
        print("=" * 60)
        print("DATA QUALITY VALIDATION")
        print("=" * 60)

        # Row count
        tables = {
            "staging.customers": 1000,
            "staging.products": 1000,
            "staging.transactions": 1000,
            "staging.transaction_items": 1000,
            "staging.marketing_campaigns": 1000,
        }

        print("\n[1] Row count validation")

        for table, minimum in tables.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]

            print(f"{table}: {count}")

            if count < minimum:
                errors.append(
                    f"{table} has fewer than {minimum} rows"
                )

        # Duplicate keys
        duplicate_checks = {
            "staging.customers": "customer_id",
            "staging.products": "product_id",
            "staging.transactions": "transaction_id",
            "staging.transaction_items": "transaction_item_id",
            "staging.marketing_campaigns": "campaign_id",
        }

        print("\n[2] Duplicate key validation")

        for table, column in duplicate_checks.items():
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM (
                    SELECT {column}
                    FROM {table}
                    GROUP BY {column}
                    HAVING COUNT(*) > 1
                ) d
                """
            )

            count = cursor.fetchone()[0]

            print(f"{table}.{column}: {count}")

            if count > 0:
                errors.append(
                    f"Duplicate keys found in {table}.{column}"
                )

        # Business rules
        print("\n[3] Business rule validation")

        cursor.execute("""
            SELECT COUNT(*)
            FROM staging.transaction_items
            WHERE quantity <= 0
        """)

        invalid_quantity = cursor.fetchone()[0]

        print(f"Invalid quantity: {invalid_quantity}")

        if invalid_quantity > 0:
            errors.append("Invalid quantity found")

        cursor.execute("""
            SELECT COUNT(*)
            FROM staging.transaction_items
            WHERE price < 0
        """)

        invalid_price = cursor.fetchone()[0]

        print(f"Invalid item price: {invalid_price}")

        if invalid_price > 0:
            errors.append("Negative transaction item price found")

        cursor.execute("""
            SELECT COUNT(*)
            FROM staging.products
            WHERE price < 0
        """)

        invalid_product_price = cursor.fetchone()[0]

        print(f"Invalid product price: {invalid_product_price}")

        if invalid_product_price > 0:
            errors.append("Negative product price found")

        # Referential integrity
        print("\n[4] Referential integrity validation")

        cursor.execute("""
            SELECT COUNT(*)
            FROM staging.transactions t
            LEFT JOIN staging.customers c
                ON t.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """)

        orphan_customers = cursor.fetchone()[0]

        print(f"Invalid customer references: {orphan_customers}")

        if orphan_customers > 0:
            errors.append("Invalid customer references found")

        cursor.execute("""
            SELECT COUNT(*)
            FROM staging.transaction_items ti
            LEFT JOIN staging.transactions t
                ON ti.transaction_id = t.transaction_id
            WHERE t.transaction_id IS NULL
        """)

        orphan_transactions = cursor.fetchone()[0]

        print(
            f"Invalid transaction references: "
            f"{orphan_transactions}"
        )

        if orphan_transactions > 0:
            errors.append("Invalid transaction references found")

        cursor.execute("""
            SELECT COUNT(*)
            FROM staging.transaction_items ti
            LEFT JOIN staging.products p
                ON ti.product_id = p.product_id
            WHERE p.product_id IS NULL
        """)

        orphan_products = cursor.fetchone()[0]

        print(f"Invalid product references: {orphan_products}")

        if orphan_products > 0:
            errors.append("Invalid product references found")

        # Transaction reconciliation
        print("\n[5] Transaction total reconciliation")

        cursor.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT
                    t.transaction_id,
                    t.total_amount,
                    SUM(ti.quantity * ti.price) AS calculated_amount
                FROM staging.transactions t
                INNER JOIN staging.transaction_items ti
                    ON t.transaction_id = ti.transaction_id
                GROUP BY
                    t.transaction_id,
                    t.total_amount
                HAVING ABS(
                    t.total_amount
                    - SUM(ti.quantity * ti.price)
                ) > 0.01
            ) x
        """)

        mismatches = cursor.fetchone()[0]

        print(f"Transaction mismatches: {mismatches}")

        if mismatches > 0:
            errors.append(
                "Transaction total reconciliation failed"
            )

        # Fact reconciliation
        print("\n[6] Fact reconciliation")

        cursor.execute("""
            SELECT COUNT(*)
            FROM staging.transaction_items
        """)

        source_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM dw.fact_sales
        """)

        fact_count = cursor.fetchone()[0]

        print(f"Source transaction items: {source_count}")
        print(f"DWH fact_sales: {fact_count}")

        if source_count != fact_count:
            errors.append(
                "Source transaction item count "
                "does not match fact_sales"
            )

        cursor.execute("""
            SELECT
                (
                    SELECT COALESCE(
                        SUM(quantity * price), 0
                    )
                    FROM staging.transaction_items
                ),
                (
                    SELECT COALESCE(
                        SUM(sales_amount), 0
                    )
                    FROM dw.fact_sales
                )
        """)

        source_amount, fact_amount = cursor.fetchone()

        print(f"Source sales amount: {source_amount}")
        print(f"DWH sales amount: {fact_amount}")

        if abs(source_amount - fact_amount) > 0.01:
            errors.append(
                "Source sales amount does not match fact_sales"
            )

        print("\n" + "=" * 60)

        if errors:
            print("VALIDATION FAILED")

            for error in errors:
                print(f"- {error}")

            raise ValueError(
                f"Validation failed with {len(errors)} issue(s)"
            )

        print("VALIDATION PASSED")
        print("=" * 60)

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    run_validation()
