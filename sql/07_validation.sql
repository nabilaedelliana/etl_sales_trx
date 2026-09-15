USE TesDE;
GO

/* =========================================================
   07_validation.sql
   Data Quality & DWH Validation
   ========================================================= */


/* =========================================================
   1. STAGING ROW COUNT
   Expected:
   customers             >= 1000
   products              >= 1000
   transactions          >= 1000
   transaction_items     >= 1000
   marketing_campaigns   >= 1000
   ========================================================= */

SELECT
    'staging.customers' AS table_name,
    COUNT(*) AS row_count
FROM staging.customers

UNION ALL

SELECT
    'staging.products',
    COUNT(*)
FROM staging.products

UNION ALL

SELECT
    'staging.transactions',
    COUNT(*)
FROM staging.transactions

UNION ALL

SELECT
    'staging.transaction_items',
    COUNT(*)
FROM staging.transaction_items

UNION ALL

SELECT
    'staging.marketing_campaigns',
    COUNT(*)
FROM staging.marketing_campaigns;


/* =========================================================
   2. DWH ROW COUNT
   ========================================================= */

SELECT
    'dw.dim_customer' AS table_name,
    COUNT(*) AS row_count
FROM dw.dim_customer

UNION ALL

SELECT
    'dw.dim_product',
    COUNT(*)
FROM dw.dim_product

UNION ALL

SELECT
    'dw.dim_date',
    COUNT(*)
FROM dw.dim_date

UNION ALL

SELECT
    'dw.dim_campaign',
    COUNT(*)
FROM dw.dim_campaign

UNION ALL

SELECT
    'dw.fact_sales',
    COUNT(*)
FROM dw.fact_sales;


/* =========================================================
   3. SOURCE VS DWH RECONCILIATION
   ========================================================= */

SELECT
    'Source transaction_items' AS metric,
    COUNT(*) AS row_count,
    SUM(quantity * price) AS total_sales
FROM staging.transaction_items

UNION ALL

SELECT
    'DWH fact_sales',
    COUNT(*),
    SUM(sales_amount)
FROM dw.fact_sales;


/* =========================================================
   4. DUPLICATE KEY CHECK
   Expected issue_count = 0
   ========================================================= */

SELECT
    'Duplicate customers.customer_id' AS check_name,
    COUNT(*) - COUNT(DISTINCT customer_id) AS issue_count
FROM staging.customers

UNION ALL

SELECT
    'Duplicate products.product_id',
    COUNT(*) - COUNT(DISTINCT product_id)
FROM staging.products

UNION ALL

SELECT
    'Duplicate transactions.transaction_id',
    COUNT(*) - COUNT(DISTINCT transaction_id)
FROM staging.transactions

UNION ALL

SELECT
    'Duplicate transaction_items.transaction_item_id',
    COUNT(*) - COUNT(DISTINCT transaction_item_id)
FROM staging.transaction_items

UNION ALL

SELECT
    'Duplicate marketing_campaigns.campaign_id',
    COUNT(*) - COUNT(DISTINCT campaign_id)
FROM staging.marketing_campaigns;


/* =========================================================
   5. NULL CHECK
   Expected issue_count = 0
   ========================================================= */

SELECT
    'NULL customer_id' AS check_name,
    COUNT(*) AS issue_count
FROM staging.customers
WHERE customer_id IS NULL

UNION ALL

SELECT
    'NULL product_id',
    COUNT(*)
FROM staging.products
WHERE product_id IS NULL

UNION ALL

SELECT
    'NULL transaction_id',
    COUNT(*)
FROM staging.transactions
WHERE transaction_id IS NULL

UNION ALL

SELECT
    'NULL transaction_item_id',
    COUNT(*)
FROM staging.transaction_items
WHERE transaction_item_id IS NULL

UNION ALL

SELECT
    'NULL transaction_id in transaction_items',
    COUNT(*)
FROM staging.transaction_items
WHERE transaction_id IS NULL

UNION ALL

SELECT
    'NULL product_id in transaction_items',
    COUNT(*)
FROM staging.transaction_items
WHERE product_id IS NULL;


/* =========================================================
   6. INVALID VALUE CHECK
   Expected issue_count = 0
   ========================================================= */

SELECT
    'Invalid quantity <= 0' AS check_name,
    COUNT(*) AS issue_count
FROM staging.transaction_items
WHERE quantity <= 0

UNION ALL

SELECT
    'Invalid transaction item price < 0',
    COUNT(*)
FROM staging.transaction_items
WHERE price < 0

UNION ALL

SELECT
    'Invalid product price < 0',
    COUNT(*)
FROM staging.products
WHERE price < 0;


/* =========================================================
   7. ORPHAN RECORD CHECK
   Expected issue_count = 0
   ========================================================= */

SELECT
    'Transaction items without transaction' AS check_name,
    COUNT(*) AS issue_count
FROM staging.transaction_items ti
LEFT JOIN staging.transactions t
    ON ti.transaction_id = t.transaction_id
WHERE t.transaction_id IS NULL

UNION ALL

SELECT
    'Transaction items without product',
    COUNT(*)
FROM staging.transaction_items ti
LEFT JOIN staging.products p
    ON ti.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT
    'Transactions without customer',
    COUNT(*)
FROM staging.transactions t
LEFT JOIN staging.customers c
    ON t.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


/* =========================================================
   8. TRANSACTION TOTAL RECONCILIATION
   Expected mismatch_count = 0
   ========================================================= */

SELECT
    COUNT(*) AS transaction_count_with_mismatch
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
        t.total_amount - SUM(ti.quantity * ti.price)
    ) > 0.01
) x;
