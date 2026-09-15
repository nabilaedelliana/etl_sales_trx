from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook


def get_connection():
    hook = MsSqlHook(mssql_conn_id="mssql_tesde")
    return hook.get_conn()


def load_dimensions():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        print("Clearing DWH dimension tables...")

        cursor.execute("DELETE FROM dw.dim_customer")
        cursor.execute("DELETE FROM dw.dim_product")
        cursor.execute("DELETE FROM dw.dim_campaign")
        cursor.execute("DELETE FROM dw.dim_date")

        print("Loading dim_customer...")

        cursor.execute("""
            INSERT INTO dw.dim_customer (
                customer_id,
                name,
                email,
                city,
                signup_date
            )
            SELECT
                customer_id,
                name,
                email,
                city,
                signup_date
            FROM staging.customers;
        """)

        print("Loading dim_product...")

        cursor.execute("""
            INSERT INTO dw.dim_product (
                product_id,
                product_name,
                category,
                price
            )
            SELECT
                product_id,
                product_name,
                category,
                price
            FROM staging.products;
        """)

        print("Loading dim_campaign...")

        cursor.execute("""
            INSERT INTO dw.dim_campaign (
                campaign_id,
                campaign_name,
                start_date,
                end_date,
                channel
            )
            SELECT
                campaign_id,
                campaign_name,
                start_date,
                end_date,
                channel
            FROM staging.marketing_campaigns;
        """)

        print("Loading dim_date...")

        cursor.execute("""
            INSERT INTO dw.dim_date (
                date_key,
                full_date,
                day,
                day_name,
                week,
                month,
                month_name,
                quarter,
                year
            )
            SELECT DISTINCT
                CONVERT(INT, CONVERT(VARCHAR(8), CAST(transaction_date AS DATE), 112)) AS date_key,
                CAST(transaction_date AS DATE) AS full_date,
                DAY(transaction_date) AS day,
                DATENAME(WEEKDAY, transaction_date) AS day_name,
                DATEPART(WEEK, transaction_date) AS week,
                MONTH(transaction_date) AS month,
                DATENAME(MONTH, transaction_date) AS month_name,
                DATEPART(QUARTER, transaction_date) AS quarter,
                YEAR(transaction_date) AS year
            FROM staging.transactions
            WHERE transaction_date IS NOT NULL;
        """)

        connection.commit()

        print("Dimensions loaded successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def load_fact():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        print("Clearing DWH fact table...")

        cursor.execute("""
            DELETE FROM dw.fact_sales
        """)

        print("Loading fact_sales...")

        cursor.execute("""
            INSERT INTO dw.fact_sales (
                transaction_id,
                transaction_item_id,
                customer_key,
                product_key,
                date_key,
                campaign_key,
                quantity,
                unit_price,
                sales_amount
            )
            SELECT
                t.transaction_id,
                ti.transaction_item_id,
                dc.customer_key,
                dp.product_key,
                dd.date_key,
                dcamp.campaign_key,
                ti.quantity,
                ti.price AS unit_price,
                ti.quantity * ti.price AS sales_amount
            FROM staging.transactions t
            INNER JOIN staging.transaction_items ti
                ON t.transaction_id = ti.transaction_id
            INNER JOIN dw.dim_customer dc
                ON t.customer_id = dc.customer_id
            INNER JOIN dw.dim_product dp
                ON ti.product_id = dp.product_id
            INNER JOIN dw.dim_date dd
                ON CAST(t.transaction_date AS DATE) = dd.full_date
            LEFT JOIN dw.dim_campaign dcamp
                ON CAST(t.transaction_date AS DATE)
                   BETWEEN dcamp.start_date AND dcamp.end_date;
        """)

        print(f"Rows inserted into fact_sales: {cursor.rowcount}")

        connection.commit()

        cursor.execute("""
            SELECT COUNT(*)
            FROM dw.fact_sales
        """)

        fact_count = cursor.fetchone()[0]

        print(f"Fact rows after commit: {fact_count}")
        print("Fact table loaded successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_dimensions()
