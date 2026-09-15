USE TesDE;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'staging'
)
BEGIN
    EXEC('CREATE SCHEMA staging');
END;
GO

IF OBJECT_ID('staging.customers', 'U') IS NULL
BEGIN
    CREATE TABLE staging.customers (
        customer_id BIGINT NOT NULL,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        city VARCHAR(100),
        signup_date DATE
    );
END;
GO

IF OBJECT_ID('staging.products', 'U') IS NULL
BEGIN
    CREATE TABLE staging.products (
        product_id BIGINT NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        category VARCHAR(100),
        price DECIMAL(18,2)
    );
END;
GO

IF OBJECT_ID('staging.transactions', 'U') IS NULL
BEGIN
    CREATE TABLE staging.transactions (
        transaction_id BIGINT NOT NULL,
        customer_id BIGINT NOT NULL,
        transaction_date DATETIME2,
        total_amount DECIMAL(18,2)
    );
END;
GO

IF OBJECT_ID('staging.transaction_items', 'U') IS NULL
BEGIN
    CREATE TABLE staging.transaction_items (
        transaction_item_id BIGINT NOT NULL,
        transaction_id BIGINT NOT NULL,
        product_id BIGINT NOT NULL,
        quantity INT NOT NULL,
        price DECIMAL(18,2)
    );
END;
GO

IF OBJECT_ID('staging.marketing_campaigns', 'U') IS NULL
BEGIN
    CREATE TABLE staging.marketing_campaigns (
        campaign_id BIGINT NOT NULL,
        campaign_name VARCHAR(255) NOT NULL,
        start_date DATE,
        end_date DATE,
        channel VARCHAR(100)
    );
END;
GO
