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
