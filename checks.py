import duckdb

CHECKS = {
    "no_null_keys_in_fact": """
        SELECT COUNT(*) FROM fact_order_items
        WHERE customer_key IS NULL OR product_key IS NULL OR date_key IS NULL
    """,
    "no_duplicate_fact_rows": """
        SELECT COUNT(*) FROM (
            SELECT order_id, order_item_id FROM fact_order_items
            GROUP BY order_id, order_item_id
            HAVING COUNT(*) > 1
        )
    """,
    "fact_rowcount_matches_staging": """
        SELECT ABS(
            (SELECT COUNT(*) FROM fact_order_items) -
            (SELECT COUNT(*) FROM stg_order_items)
        )
    """,
    "no_duplicate_customers_in_dim": """
        SELECT COUNT(*) FROM (
            SELECT customer_id FROM dim_customer
            GROUP BY customer_id HAVING COUNT(*) > 1
        )
    """,
    "no_negative_prices": """
        SELECT COUNT(*) FROM fact_order_items WHERE price < 0
    """,
    "all_dates_exist_in_dim_date": """
        SELECT COUNT(*) FROM fact_order_items f
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.date_key IS NULL
    """,
}


def run_all():
    con = duckdb.connect("warehouse.duckdb", read_only=True)
    results = {}
    for name, sql in CHECKS.items():
        results[name] = con.execute(sql).fetchone()[0]
    con.close()
    return results


if __name__ == "__main__":
    for name, bad_rows in run_all().items():
        status = "PASS" if bad_rows == 0 else "FAIL"
        print(f"{status}  {name}  (bad rows: {bad_rows})")