"""
Load the Olist CSVs into DuckDB and expose the analysis queries as DataFrames.

The app and the notebook both import from here, so all your SQL lives in one
place. Add new query functions as you discover findings in Week 2.
"""
from pathlib import Path
import duckdb
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# Clean table name -> Olist CSV filename
TABLES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open an in-memory DuckDB, load the CSVs, and build the delivery base table."""
    con = duckdb.connect()
    for table, fname in TABLES.items():
        path = DATA_DIR / fname
        if not path.exists():
            raise FileNotFoundError(
                f"Missing '{fname}' in the data/ folder.\n"
                "Download the Olist dataset from Kaggle and drop the CSVs into data/. "
                "See data/PUT_CSVS_HERE.md."
            )
        con.execute(
            f"CREATE TABLE {table} AS "
            f"SELECT * FROM read_csv_auto('{path.as_posix()}')"
        )
    _build_delivery_base(con)
    return con


def _build_delivery_base(con: duckdb.DuckDBPyConnection) -> None:
    """One row per *delivered* order, with delivery time and a late flag.

    This is the base table everything else hangs off — the SQL equivalent of
    your Week 1 Day 3 CTE, materialised so the app can reuse it.
    """
    con.execute(
        """
        CREATE OR REPLACE TABLE delivery AS
        SELECT
            o.order_id,
            o.customer_id,
            date_diff('day', o.order_purchase_timestamp,
                             o.order_delivered_customer_date)      AS days_to_deliver,
            date_diff('day', o.order_estimated_delivery_date,
                             o.order_delivered_customer_date)      AS days_vs_estimate,
            CASE WHEN o.order_delivered_customer_date
                      > o.order_estimated_delivery_date
                 THEN 1 ELSE 0 END                                 AS is_late,
            date_trunc('month', o.order_purchase_timestamp)        AS purchase_month
        FROM orders o
        WHERE o.order_status = 'delivered'
          AND o.order_delivered_customer_date IS NOT NULL;
        """
    )


def get_kpis(con: duckdb.DuckDBPyConnection) -> dict:
    """Top-line numbers for the dashboard header."""
    total, on_time_pct, avg_days = con.execute(
        """
        SELECT
            COUNT(*)                          AS total_delivered,
            ROUND(AVG(1 - is_late) * 100, 1)  AS on_time_pct,
            ROUND(AVG(days_to_deliver), 1)    AS avg_days_to_deliver
        FROM delivery;
        """
    ).fetchone()
    (avg_review,) = con.execute(
        "SELECT ROUND(AVG(review_score), 2) FROM order_reviews"
    ).fetchone()
    return {
        "total_delivered": total,
        "on_time_pct": on_time_pct,
        "avg_days_to_deliver": avg_days,
        "avg_review_score": avg_review,
    }


def get_review_vs_late(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """The core finding: average review score for on-time vs late orders."""
    return con.execute(
        """
        SELECT
            CASE WHEN d.is_late = 1 THEN 'Late' ELSE 'On time' END AS delivery_status,
            COUNT(*)                       AS n_orders,
            ROUND(AVG(r.review_score), 2)  AS avg_review_score
        FROM delivery d
        JOIN order_reviews r ON d.order_id = r.order_id
        GROUP BY 1
        ORDER BY 1;
        """
    ).df()


def get_late_by_category(con: duckdb.DuckDBPyConnection,
                         min_orders: int = 100) -> pd.DataFrame:
    """Late-delivery rate per category (grain = order-item, since an order can
    span multiple categories). HAVING drops low-sample noise."""
    return con.execute(
        """
        SELECT
            t.product_category_name_english AS category,
            COUNT(*)                        AS n_orders,
            ROUND(AVG(d.is_late) * 100, 1)  AS late_pct
        FROM delivery d
        JOIN order_items i ON d.order_id = i.order_id
        JOIN products    p ON i.product_id = p.product_id
        JOIN category_translation t
             ON p.product_category_name = t.product_category_name
        GROUP BY category
        HAVING COUNT(*) >= ?
        ORDER BY late_pct DESC;
        """,
        [min_orders],
    ).df()


if __name__ == "__main__":
    # Quick smoke test: `python src/data_loader.py`
    conn = get_connection()
    print("KPIs:", get_kpis(conn))
    print(get_review_vs_late(conn))
