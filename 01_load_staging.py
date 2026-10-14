import duckdb

con = duckdb.connect("warehouse.duckdb")

files = {
    "stg_customers": "data/olist_customers_dataset.csv",
    "stg_orders": "data/olist_orders_dataset.csv",
    "stg_order_items": "data/olist_order_items_dataset.csv",
    "stg_products": "data/olist_products_dataset.csv",
    "stg_category_translation": "data/product_category_name_translation.csv",
}

for table, path in files.items():
    con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto('{path}')")
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(table, "->", count, "rows")

con.close()