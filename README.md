# Data Engineering Test

## Overview

This project implements an end-to-end data engineering pipeline for processing sales and marketing data.

The solution covers:

* Synthetic data generation
* Data validation and staging
* ETL orchestration using Apache Airflow
* Data warehouse modeling using a star schema
* Loading data into Microsoft SQL Server
* Data quality and reconciliation checks
* Architecture and data modeling documentation

## Architecture

The overall data flow is:

```text
Python Data Generator
        |
        v
    Raw CSV Files
        |
        v
   Apache Airflow
        |
        v
SQL Server - Staging
        |
        v
SQL Server - Data Warehouse
        |
        +------------------+
        |                  |
        v                  v
   Star Schema        Data Validation
        |
        v
 Analytics / BI
```

## Technology Stack

* Python 3
* Apache Airflow
* Pandas
* Microsoft SQL Server
* SQL Server Management Studio (SSMS)
* PyODBC / Airflow Microsoft SQL Server Provider
* draw.io
* Git / GitHub

## Project Structure

```text
data-engineering-test/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── transactions.csv
│   │   ├── transaction_items.csv
│   │   └── marketing_campaigns.csv
│   └── processed/
│       ├── dim_customer.csv
│       ├── dim_product.csv
│       ├── dim_date.csv
│       ├── dim_campaign.csv
│       └── fact_sales.csv
│
├── dags/
│   └── sales_etl_dag.py
│
├── scripts/
│   ├── generate_data.py
│   ├── validate_data.py
│   ├── load_staging.py
│   └── load_dwh.py
│   └── streaming_transaction.py
│
├── sql/
│   ├── 01_create_database.sql
│   ├── 02_create_staging.sql
│   ├── 03_create_dimensions.sql
│   ├── 04_create_fact.sql
│   ├── 05_load_dimensions.sql
│   ├── 06_load_fact.sql
│   └── 07_validation.sql
│
├── diagrams/
│   ├── erd_data_modelling.drawio
│   ├── erd_data_modelling.png
│   ├── erd_architecture.drawio
│   └── erd_architecture.png
│   ├── streaming_architecture.drawio
│   └── streaming_architecture.png
│
└── docs/
    └── data_modeling.md
```

## Source Data

Five source datasets are generated as CSV files.

| Table               | Description                    | Records |
| ------------------- | ------------------------------ | ------: |
| customers           | Customer information           |   1,000 |
| products            | Product information            |   1,000 |
| transactions        | Transaction headers            |   2,000 |
| transaction_items   | Transaction line items         |   5,893 |
| marketing_campaigns | Marketing campaign information |   1,000 |

The data is synthetic and generated using Python.

## ETL Pipeline

Apache Airflow is used to orchestrate the ETL process.

The main DAG is:

```text
start
  |
  v
generate_data
  |
  +----> load_customers
  |
  +----> load_products
  |
  +----> load_transactions
  |
  +----> load_transaction_items
  |
  +----> load_marketing_campaigns
             |
             v
      load_dimensions
             |
             v
         load_fact
             |
             v
            end
```

The five staging tables are loaded in parallel because they are independent source datasets.

After staging is completed, the dimension tables are populated before loading the fact table.

## Data Warehouse Model

The data warehouse uses a **star schema**.

### Fact Table

`dw.fact_sales`

The grain of the fact table is:

> One row per transaction item.

Main measures:

* quantity
* unit_price
* sales_amount

Foreign keys connect the fact table to the dimension tables.

### Dimension Tables

* `dw.dim_customer`
* `dw.dim_product`
* `dw.dim_date`
* `dw.dim_campaign`

Surrogate keys are used for the dimension tables to separate warehouse keys from the source system identifiers.

The detailed data modeling explanation is available in:

`docs/data_modeling.md`

## Campaign Attribution

The source `transactions` table does not contain a `campaign_id`.

Therefore, campaign attribution is implemented using the transaction date:

```text
transaction_date BETWEEN campaign start_date AND end_date
```

Campaign periods are generated without overlapping active periods so that a transaction can be associated with at most one campaign.

This assumption allows the campaign dimension to be integrated into the sales fact without modifying the original source table structure.

## Data Quality

The pipeline includes validation checks for:

* Minimum source row count
* Duplicate business keys
* Null values
* Invalid quantity values
* Invalid prices
* Orphan customer references
* Orphan product references
* Orphan transaction references
* Orphan date references
* Transaction total reconciliation
* Fact row count reconciliation
* Sales amount reconciliation

### Validation Result

| Check               |            Result |
| ------------------- | ----------------: |
| Customers           |             1,000 |
| Products            |             1,000 |
| Transactions        |             2,000 |
| Transaction Items   |             5,893 |
| Marketing Campaigns |             1,000 |
| Fact Sales          |             5,893 |
| Source Sales Amount | 43,135,039,033.54 |
| DWH Sales Amount    | 43,135,039,033.54 |
| Data Quality Issues |                 0 |

The source transaction item count and DWH fact row count are identical, and the total sales amount is fully reconciled.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/nabilaedelliana/etl_sales_trx.git
cd etl_sales_trx
```

### 2. Install Python dependencies

Create and activate a Python virtual environment:

```bash
python -m venv airflow-env
source airflow-env/bin/activate
```
Install the project dependencies:
```
pip install -r requirements.txt
```
### 3. Configure SQL Server

Create the database and schemas using the SQL scripts in the `sql/` directory.
The project uses a SQL Server database named `TesDE`.

Execute the scripts in the following order:

```text
01_create_database.sql
02_create_staging.sql
03_create_dimensions.sql
04_create_fact.sql
```

### 4. Configure Airflow
Initialize Airflow if it has not been initialized:

```bash
airflow db migrate
```

Create an Airflow connection for SQL Server:

```text
Connection ID: mssql_tesde
Connection Type: Microsoft SQL Server
Host: <SQL_SERVER_HOST>
Port: 1433
Database/Schema: TesDE
Username: <SQL_USERNAME>
Password: <SQL_PASSWORD>
```

The credentials should be configured locally and should not be committed to GitHub.
The DAG uses the connection ID `mssql_tesde` to connect to SQL Server.

### 5. Run the Airflow DAG

Ensure the DAG file is available in the Airflow DAG directory:

```text
dags/sales_etl_dag.py
```

Then trigger the DAG from the Airflow UI or CLI:

```bash
airflow dags trigger sales_etl
```

The DAG executes the complete pipeline from data generation through DWH fact loading.


## Data Validation

After the pipeline completes, data quality can be validated using the SQL validation queries or the Python validation script.

### SQL Validation

The SQL validation queries are available in:

```text
sql/07_validation.sql
```
These queries verify row counts, referential integrity, duplicates, invalid values, and reconciliation between source and warehouse data.

### Python Validation
The automated validation script can be executed using:
```bash
python scripts/validate_data.py
```
The script validates row counts, duplicate keys, business rules, referential integrity, transaction total reconciliation, and source-to-DWH fact reconciliation.

The latest validation result:
```
VALIDATION PASSED
```

## Design Decisions

### Why Airflow?

Apache Airflow is used as the orchestration layer because the assignment requires Python and Airflow. It provides task dependency management, scheduling, monitoring, and retry capabilities.

### Why SQL Server?

SQL Server is used as the relational database for both staging and data warehouse layers. It also provides strong support for SQL-based transformations, constraints, and analytical workloads.

### Why a Star Schema?

A star schema simplifies analytical queries by separating measurable business events from descriptive dimensions. It also provides a scalable structure for BI and reporting use cases.

### Why Surrogate Keys?

Surrogate keys provide stable warehouse identifiers and decouple the data warehouse model from source-system identifiers.

## Diagrams

### Data Modeling / ERD

The data modeling diagram shows the source staging tables and the DWH star schema.

Files:

```text
diagrams/erd_data_modelling.drawio
diagrams/erd_data_modelling.png
```

### Architecture

The architecture diagram illustrates the end-to-end flow from raw data generation through Airflow, staging, DWH, and analytics.

Files:

```text
diagrams/erd_architecture.drawio
diagrams/erd_architecture.png
```

## Assumptions

1. All generated source datasets are synthetic.
2. Each source table contains at least 1,000 records.
3. The fact table grain is one row per transaction item.
4. Transaction items reference valid transactions and products.
5. Campaign attribution is based on transaction date because the source transaction table does not contain a campaign identifier.
6. Campaign periods do not overlap.
7. SQL Server is used as the local relational database and data warehouse.
8. Airflow credentials and database passwords are managed locally and are excluded from source control.

## Future Improvement

For a production implementation, the pipeline could be extended with:

* Incremental loading
* Slowly Changing Dimensions (SCD)
* Centralized configuration management
* Automated alerting
* Data quality frameworks
* CI/CD
* Cloud object storage
* Streaming ingestion using Kafka

## Optional Streaming Pipeline

This project also includes an optional simple real-time streaming pipeline.

The pipeline consists of:

```text
Dummy Transaction Generator
            ↓
       Python Stream
            ↓
Aggregate Transaction Count
         Per Minute
            ↓
      Console Output
```
### Components
* Source: Python dummy transaction generator
* Processing: Aggregate transaction count per minute
* Sink: Console output
* Implementation: scripts/streaming_transaction.py
* Architecture Diagram: diagrams/streaming_architecture.drawio
* Architecture Preview: diagrams/streaming_architecture.png
* Pipeline Documentation: docs/streaming.md

### Run Streaming Pipeline
```bash
python scripts/streaming_transaction.py`
```

The pipeline runs continuously and can be stopped using `Ctrl + C`.

Example output:
```
2026-09-16 15:51 | Transactions: 43
```
For more details about the implementation and design choices, see:
```
docs/streaming.md
```

---

**Author:** Nabila Edelliana Khairunnisa

