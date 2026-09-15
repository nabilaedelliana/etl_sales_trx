-- Load Customer Dimension
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


-- Load Product Dimension
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


-- Load Campaign Dimension
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


-- Load Date Dimension
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
    CONVERT(INT, CONVERT(VARCHAR(8), CAST(transaction_date AS DATE), 112)),
    CAST(transaction_date AS DATE),
    DAY(transaction_date),
    DATENAME(WEEKDAY, transaction_date),
    DATEPART(WEEK, transaction_date),
    MONTH(transaction_date),
    DATENAME(MONTH, transaction_date),
    DATEPART(QUARTER, transaction_date),
    YEAR(transaction_date)
FROM staging.transactions
WHERE transaction_date IS NOT NULL;
