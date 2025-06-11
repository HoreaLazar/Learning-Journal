CREATE TABLE dbo.sales
(
    record_id int IDENTITY(1,1) NOT NULL,
    invoice_id VARCHAR(20),
    branch CHAR(1),
    city VARCHAR(50),
    customer_type VARCHAR(20),
    gender VARCHAR(10),
    productLine VARCHAR(50),
    unit_price DECIMAL(10, 2),
    quantity INT,
    tax DECIMAL(10, 4),
    total DECIMAL(10, 4),
    sale_date DATE,
    sale_time TIME,
    payment VARCHAR(20),
    cogs DECIMAL(10, 2),
    gross_margin_percentage DECIMAL(5, 4),
    gross_income DECIMAL(10, 4),
    rating DECIMAL(3, 1)
)
GO
CREATE CLUSTERED INDEX IX_record_id ON dbo.sales (record_id);