import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)

queries = {
    "Monthly revenue and month-over-month growth": """
        WITH monthly AS (
            SELECT d.year, d.month, ROUND(SUM(f.price), 2) AS revenue
            FROM fact_order_items f
            JOIN dim_date d ON f.date_key = d.date_key
            WHERE f.order_status = 'delivered'
            AND d.year >= 2017
            GROUP BY d.year, d.month
        )
        SELECT year, month, revenue,
               ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year, month))
                     / LAG(revenue) OVER (ORDER BY year, month), 1) AS mom_growth_pct
        FROM monthly
        ORDER BY year, month
    """,
    "Top 5 product categories by revenue": """
        SELECT p.category, ROUND(SUM(f.price), 2) AS revenue
        FROM fact_order_items f
        JOIN dim_product p ON f.product_key = p.product_key
        WHERE f.order_status = 'delivered'
        GROUP BY p.category
        ORDER BY revenue DESC
        LIMIT 5
    """,
    "States ranked by revenue": """
        SELECT c.customer_state,
               ROUND(SUM(f.price), 2) AS revenue,
               RANK() OVER (ORDER BY SUM(f.price) DESC) AS revenue_rank
        FROM fact_order_items f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        WHERE f.order_status = 'delivered'
        GROUP BY c.customer_state
        ORDER BY revenue_rank
        LIMIT 10
    """,
    "Running total of revenue by month": """
        WITH monthly AS (
            SELECT d.year, d.month, SUM(f.price) AS revenue
            FROM fact_order_items f
            JOIN dim_date d ON f.date_key = d.date_key
            WHERE f.order_status = 'delivered'
            GROUP BY d.year, d.month
        )
        SELECT year, month, ROUND(revenue, 2) AS revenue,
               ROUND(SUM(revenue) OVER (ORDER BY year, month), 2) AS running_total
        FROM monthly
        ORDER BY year, month
    """,
}

for title, sql in queries.items():
    print("\n" + title)
    print(con.execute(sql).df().to_string(index=False))

con.close()