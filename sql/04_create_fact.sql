USE TesDE;
GO

/* =========================================================
   Fact: Sales
   Grain:
   One row per transaction item
   ========================================================= */

IF OBJECT_ID('dw.fact_sales', 'U') IS NULL
BEGIN
    CREATE TABLE dw.fact_sales (
        sales_key BIGINT IDENTITY(1,1) NOT NULL,

        transaction_id BIGINT NOT NULL,
        transaction_item_id BIGINT NOT NULL,

        customer_key INT NOT NULL,
        product_key INT NOT NULL,
        date_key INT NOT NULL,
        campaign_key INT NULL,

        quantity INT NOT NULL,
        unit_price DECIMAL(18,2) NOT NULL,
        sales_amount DECIMAL(18,2) NOT NULL,

        CONSTRAINT PK_fact_sales
            PRIMARY KEY (sales_key),

        CONSTRAINT UQ_fact_sales_transaction_item
            UNIQUE (transaction_item_id),

        CONSTRAINT FK_fact_sales_customer
            FOREIGN KEY (customer_key)
            REFERENCES dw.dim_customer(customer_key),

        CONSTRAINT FK_fact_sales_product
            FOREIGN KEY (product_key)
            REFERENCES dw.dim_product(product_key),

        CONSTRAINT FK_fact_sales_date
            FOREIGN KEY (date_key)
            REFERENCES dw.dim_date(date_key),

        CONSTRAINT FK_fact_sales_campaign
            FOREIGN KEY (campaign_key)
            REFERENCES dw.dim_campaign(campaign_key),

        CONSTRAINT CK_fact_sales_quantity
            CHECK (quantity > 0),

        CONSTRAINT CK_fact_sales_unit_price
            CHECK (unit_price >= 0),

        CONSTRAINT CK_fact_sales_sales_amount
            CHECK (sales_amount >= 0)
    );
END;
GO
