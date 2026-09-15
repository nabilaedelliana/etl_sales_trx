USE TesDE;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'dw'
)
BEGIN
    EXEC('CREATE SCHEMA dw');
END;
GO


/* =========================================================
   Dimension: Customer
   ========================================================= */

IF OBJECT_ID('dw.dim_customer', 'U') IS NULL
BEGIN
    CREATE TABLE dw.dim_customer (
        customer_key INT IDENTITY(1,1) NOT NULL,
        customer_id BIGINT NOT NULL,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        city VARCHAR(100),
        signup_date DATE,

        CONSTRAINT PK_dim_customer
            PRIMARY KEY (customer_key),

        CONSTRAINT UQ_dim_customer_customer_id
            UNIQUE (customer_id)
    );
END;
GO


/* =========================================================
   Dimension: Product
   ========================================================= */

IF OBJECT_ID('dw.dim_product', 'U') IS NULL
BEGIN
    CREATE TABLE dw.dim_product (
        product_key INT IDENTITY(1,1) NOT NULL,
        product_id BIGINT NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        category VARCHAR(100),
        price DECIMAL(18,2),

        CONSTRAINT PK_dim_product
            PRIMARY KEY (product_key),

        CONSTRAINT UQ_dim_product_product_id
            UNIQUE (product_id)
    );
END;
GO


/* =========================================================
   Dimension: Date
   ========================================================= */

IF OBJECT_ID('dw.dim_date', 'U') IS NULL
BEGIN
    CREATE TABLE dw.dim_date (
        date_key INT NOT NULL,
        full_date DATE NOT NULL,
        day INT NOT NULL,
        day_name VARCHAR(20) NOT NULL,
        week INT NOT NULL,
        month INT NOT NULL,
        month_name VARCHAR(20) NOT NULL,
        quarter INT NOT NULL,
        year INT NOT NULL,

        CONSTRAINT PK_dim_date
            PRIMARY KEY (date_key),

        CONSTRAINT UQ_dim_date_full_date
            UNIQUE (full_date)
    );
END;
GO


/* =========================================================
   Dimension: Campaign
   ========================================================= */

IF OBJECT_ID('dw.dim_campaign', 'U') IS NULL
BEGIN
    CREATE TABLE dw.dim_campaign (
        campaign_key INT IDENTITY(1,1) NOT NULL,
        campaign_id BIGINT NOT NULL,
        campaign_name VARCHAR(255) NOT NULL,
        start_date DATE,
        end_date DATE,
        channel VARCHAR(100),

        CONSTRAINT PK_dim_campaign
            PRIMARY KEY (campaign_key),

        CONSTRAINT UQ_dim_campaign_campaign_id
            UNIQUE (campaign_id)
    );
END;
GO


