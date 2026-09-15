# Data Modeling

## 1. Overview

The data warehouse is designed using a **star schema** to support analytical queries for sales, customers, products, dates, and marketing campaigns.

The pipeline uses the following layers:

```text
Raw CSV
   |
   v
Staging
   |
   v
Dimension Tables + Fact Table
   |
   v
Analytics / Reporting
```

## 2. Staging Layer

The staging layer stores the source data with minimal transformation.

### Source tables

- `staging.customers`
- `staging.products`
- `staging.transactions`
- `staging.transaction_items`
- `staging.marketing_campaigns`

The staging layer is used as the landing area before data is transformed and loaded into the dimensional model.

## 3. Data Warehouse Model

The DWH consists of four dimension tables and one fact table:

- `dw.dim_customer`
- `dw.dim_product`
- `dw.dim_date`
- `dw.dim_campaign`
- `dw.fact_sales`

### Star schema

```text
                 dim_customer
                      |
                      |
dim_product ---- fact_sales ---- dim_date
                      |
                      |
                 dim_campaign
```

## 4. Fact Table

### `dw.fact_sales`

The fact table stores sales transaction-item level data.

### Fact grain

**One row in `fact_sales` represents one transaction item.**

This grain was selected because the source contains `transaction_items`, where each item belongs to a transaction and references a product.

### Columns

| Column | Description |
|---|---|
| `sales_key` | Surrogate primary key |
| `transaction_id` | Source transaction identifier |
| `transaction_item_id` | Source transaction-item identifier |
| `customer_key` | Foreign key to `dim_customer` |
| `product_key` | Foreign key to `dim_product` |
| `date_key` | Foreign key to `dim_date` |
| `campaign_key` | Nullable foreign key to `dim_campaign` |
| `quantity` | Quantity purchased |
| `unit_price` | Price per item |
| `sales_amount` | Calculated as `quantity * unit_price` |

## 5. Dimension Tables

### `dw.dim_customer`

Stores customer attributes used for customer-level analysis.

The table uses `customer_key` as a surrogate primary key while retaining the source `customer_id` as the business identifier.

### `dw.dim_product`

Stores product attributes such as product name, category, and price.

`product_key` is the surrogate primary key and `product_id` is retained as the source business identifier.

### `dw.dim_date`

Provides calendar attributes for time-based analysis.

The `date_key` is generated in `YYYYMMDD` format.

Attributes include:

- Full date
- Day
- Day name
- Week
- Month
- Month name
- Quarter
- Year

### `dw.dim_campaign`

Stores marketing campaign information including campaign name, active period, and channel.

`campaign_key` is the surrogate primary key and `campaign_id` is retained as the source business identifier.

## 6. Surrogate Keys

Surrogate keys are used for DWH dimensions:

- `customer_key`
- `product_key`
- `date_key`
- `campaign_key`

The fact table references these surrogate keys rather than relying only on source identifiers.

Benefits include:

- Separation between source identifiers and DWH identifiers
- More stable relationships between facts and dimensions
- Better support for future dimension history or source-system changes
- Consistent star-schema design

## 7. Campaign Attribution Assumption

The source `transactions` table does not contain a `campaign_id`.

Therefore, campaign attribution is derived using the transaction date:

```sql
transaction_date BETWEEN campaign.start_date AND campaign.end_date
```

This means a transaction is associated with the campaign whose active period contains the transaction date.

The generated campaign periods are assumed to be **non-overlapping**. This prevents one transaction from being associated with multiple campaigns.

`campaign_key` is nullable because a transaction may occur outside all campaign periods.

## 8. Data Quality and Reconciliation

The pipeline includes validation checks for:

- Minimum source row counts
- Duplicate source keys
- Null values in required fields
- Invalid quantity or price values
- Orphan foreign-key relationships
- Source-to-DWH row-count reconciliation
- Source-to-DWH sales-amount reconciliation
- Transaction total reconciliation

For the generated dataset, the final validation results were:

| Check | Result |
|---|---:|
| Customers | 1,000 |
| Products | 1,000 |
| Transactions | 2,000 |
| Transaction items | 5,893 |
| Marketing campaigns | 1,000 |
| Fact sales | 5,893 |
| Source sales amount | 43,135,039,033.54 |
| DWH sales amount | 43,135,039,033.54 |
| Data quality issues | 0 |

The source `transaction_items` count and `fact_sales` count reconcile exactly, and the total sales amount also reconciles.

## 9. Design Rationale

A star schema was selected because the main analytical use case is sales reporting.

The model allows analysis by:

- Customer
- Product
- Date
- Marketing campaign

while keeping measurable sales data centralized in `fact_sales`.

This structure also simplifies BI queries because analytical dimensions are directly connected to the central fact table.
