from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import PythonOperator


def load_staging_task(source_name):
    def _load():
        import sys

        sys.path.insert(
            0,
            "/home/edelliana/data-engineering-test/scripts"
        )

        from load_staging import load_csv_to_staging

        load_csv_to_staging(source_name)

    return _load


def load_dimensions_task():
    import sys

    sys.path.insert(
        0,
        "/home/edelliana/data-engineering-test/scripts"
    )

    from load_dwh import load_dimensions

    load_dimensions()


def load_fact_task():
    import sys

    sys.path.insert(
        0,
        "/home/edelliana/data-engineering-test/scripts"
    )

    from load_dwh import load_fact

    load_fact()


with DAG(
    dag_id="sales_etl",
    start_date=datetime(2026, 9, 15),
    schedule=None,
    catchup=False,
    tags=["data-engineering-test"],
) as dag:

    start = EmptyOperator(
        task_id="start"
    )

    def generate_data_task():
        import subprocess

        subprocess.run(
            [
                "python",
                "/home/edelliana/data-engineering-test/scripts/generate_data.py"
            ],
            check=True,
        )


    generate_data = PythonOperator(
        task_id="generate_data",
        python_callable=generate_data_task,
    )
    load_customers = PythonOperator(
        task_id="load_customers",
        python_callable=load_staging_task("customers"),
    )

    load_products = PythonOperator(
        task_id="load_products",
        python_callable=load_staging_task("products"),
    )

    load_transactions = PythonOperator(
        task_id="load_transactions",
        python_callable=load_staging_task("transactions"),
    )

    load_transaction_items = PythonOperator(
        task_id="load_transaction_items",
        python_callable=load_staging_task("transaction_items"),
    )

    load_marketing_campaigns = PythonOperator(
        task_id="load_marketing_campaigns",
        python_callable=load_staging_task("marketing_campaigns"),
    )
    load_dimensions = PythonOperator(
        task_id="load_dimensions",
        python_callable=load_dimensions_task,
    )
    load_fact = PythonOperator(
        task_id="load_fact",
        python_callable=load_fact_task,
    )
    end = EmptyOperator(
        task_id="end"
    )

    start >> generate_data

    generate_data >> [
        load_customers,
        load_products,
        load_transactions,
        load_transaction_items,
        load_marketing_campaigns,
    ]

    [
        load_customers,
        load_products,
        load_transactions,
        load_transaction_items,
        load_marketing_campaigns,
    ] >> load_dimensions >> load_fact >> end
