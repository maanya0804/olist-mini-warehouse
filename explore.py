import duckdb

con = duckdb.connect("warehouse.duckdb")
for t in ["stg_customers", "stg_orders", "stg_order_items", "stg_products", "stg_category_translation"]:
    print(t)
    print(con.execute(f"DESCRIBE {t}").df()[["column_name", "column_type"]])
    print()