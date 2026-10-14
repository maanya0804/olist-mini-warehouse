# Mini Data Warehouse for E-Commerce Orders

A small ETL project in Python and SQL. It loads the Olist Brazilian e-commerce CSV files into a DuckDB database, builds a star schema, runs data-quality checks, and answers a few business questions with SQL.

**Tools:** Python, SQL, DuckDB, pandas, pytest

## What the pipeline does

1. **Staging:** 5 raw CSV tables (about 344K rows in total) are loaded into the database as they are.
2. **Warehouse:** the staging tables are turned into a star schema with one fact table and three dimension tables.
3. **Checks:** 6 SQL data-quality checks run on the warehouse, both as a script and as pytest tests.
4. **Analysis:** 4 SQL queries (CTEs and window functions) answer business questions.

## Star schema

```
                 dim_date
                (1,096 rows)
                    |
                    | date_key
                    |
dim_customer ---- fact_order_items ---- dim_product
(99,441 rows)      (112,650 rows)       (32,951 rows)
```

- **Fact table grain:** one row per item in an order (order_id + order_item_id). It stores price, freight value and order status.
- **dim_customer:** customer key, city, state.
- **dim_product:** product key, English category name (missing categories are set to `unknown`), weight.
- **dim_date:** one row per day from 2016-01-01 to 2018-12-31. It is generated in SQL, not loaded from a CSV.

## Files

```
01_load_staging.py       loads the CSVs into staging tables
explore.py               prints staging column names and types
02_build_warehouse.py    builds the dimension and fact tables
checks.py                data-quality checks (SQL)
test_checks.py           runs the checks with pytest
03_analysis.py           analysis queries
requirements.txt
```

## Data

The dataset is not included in this repo. Download "Brazilian E-Commerce Public Dataset by Olist" from Kaggle and put these files in a folder called `data/`:

- olist_customers_dataset.csv
- olist_orders_dataset.csv
- olist_order_items_dataset.csv
- olist_products_dataset.csv
- product_category_name_translation.csv

## How to run

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python 01_load_staging.py
python 02_build_warehouse.py
python checks.py
pytest -v
python 03_analysis.py
```

(On Mac/Linux, activate with `source venv/bin/activate`.)

## Data-quality checks

Each check counts bad rows. Zero means the check passes. All 6 pass on the current data.

| Check | What it looks for |
|---|---|
| no_null_keys_in_fact | fact rows with no matching customer, product or date |
| no_duplicate_fact_rows | repeated (order_id, order_item_id) pairs |
| fact_rowcount_matches_staging | rows lost or duplicated by the joins |
| no_duplicate_customers_in_dim | repeated customers in dim_customer |
| no_negative_prices | prices below zero |
| all_dates_exist_in_dim_date | fact dates missing from dim_date |

## Results

Revenue below means item price for delivered orders only (freight is not included). Values are in Brazilian real (R$). Delivered revenue in the data runs from Sep 2016 to Aug 2018.

- **Total:** about R$13.2M.
- **Top categories:** health_beauty (about R$1.23M), then watches_gifts and bed_bath_table.
- **By state:** SP is highest at about R$5.07M, roughly 38% of the total, followed by RJ and MG.
- **Monthly revenue:** about R$112K in Jan 2017 and about R$925K in Jan 2018.
- Month-over-month growth is calculated from 2017 onward. 2016 has only three months of data with gaps, and `LAG` compares rows, not calendar months, so the 2016 growth values were misleading.

## Design choices

- **Star schema:** keeps analysis queries to a few joins from one fact table.
- **LEFT JOINs when building the fact table:** rows with no match stay in as NULL keys, so the checks can catch them. An INNER JOIN would drop them silently.
- **`CREATE OR REPLACE` for every table:** each run rebuilds everything, so running the pipeline twice does not create duplicates.
- **Delivered orders only in the revenue queries:** so cancelled or unavailable orders do not count as revenue.

## Limitations

- Every run is a full rebuild. It does not load only new data.
- `dim_customer` uses `customer_id`, which Olist creates per order, so it has one row per order (99,441). Repeat-customer analysis would need `customer_unique_id`.
- It runs on one machine on a fixed dataset, with no scheduling.
- Dimensions do not keep history (no slowly changing dimensions).