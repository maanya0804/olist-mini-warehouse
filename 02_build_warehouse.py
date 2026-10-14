import duckdb

con = duckdb.connect("warehouse.duckdb")

con.execute("""
    CREATE OR REPLACE TABLE dim_customer AS
    SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state
    FROM stg_customers
""")

con.execute("""
    CREATE OR REPLACE TABLE dim_product AS
    SELECT
    ROW_NUMBER() OVER (ORDER BY p.product_id) AS product_key,
    p.product_id,
    COALESCE(t.product_category_name_english, 'unknown') AS category,
    p.product_weight_g
FROM stg_products p
LEFT JOIN stg_category_translation t
    ON p.product_category_name = t.product_category_name
""")

con.execute("""
CREATE OR REPLACE TABLE dim_date AS
SELECT
    CAST(strftime(d, '%Y%m%d') AS INTEGER) AS date_key,
    CAST(d AS DATE) AS full_date,
    year(d) AS year,
    month(d) AS month,
    monthname(d) AS month_name,
    dayname(d) AS day_name
FROM generate_series(DATE '2016-01-01', DATE '2018-12-31', INTERVAL 1 DAY) AS t(d)
""")

con.execute("""
CREATE OR REPLACE TABLE fact_order_items AS
SELECT
    oi.order_id,
    oi.order_item_id,
    c.customer_key,
    p.product_key,
    CAST(strftime(CAST(o.order_purchase_timestamp AS TIMESTAMP), '%Y%m%d') AS INTEGER) AS date_key,
    o.order_status,
    oi.price,
    oi.freight_value
FROM stg_order_items oi
LEFT JOIN stg_orders o ON oi.order_id = o.order_id
LEFT JOIN dim_customer c ON o.customer_id = c.customer_id
LEFT JOIN dim_product p ON oi.product_id = p.product_id
""")

for t in ["dim_customer", "dim_product", "dim_date", "fact_order_items"]:
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(t, "->", n, "rows")

con.close()