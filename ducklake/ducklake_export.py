import os
import duckdb
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).parent.parent.parent
CATALOG   = (BASE_DIR / "lake" / "Catalog.ducklake").as_posix()
DATA_PATH = (BASE_DIR / "lake" / "lake_data").as_posix()

PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5433")
PG_URL  = f"postgresql+psycopg2://postgres:password123@{PG_HOST}:{PG_PORT}/crypto_db"

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_pg_engine():
    return create_engine(PG_URL)

def read_gold_table(engine, table: str) -> pd.DataFrame:
    return pd.read_sql(f"SELECT * FROM analytics_gold.{table}", engine)

def print_snapshots(con, catalog_alias: str = "lake"):
    print(f"\n{'─'*55}")
    print(f"  Snapshots in '{catalog_alias}'")
    print(f"{'─'*55}")
    rows = con.execute(f"""
        SELECT snapshot_id,
               snapshot_time::VARCHAR AS snapshot_time,
               schema_version,
               changes
        FROM ducklake_snapshots('{catalog_alias}');
    """).fetchall()
    for r in rows:
        print(" ", r)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # 1. Create folders if they don't exist
    Path(CATALOG).parent.mkdir(parents=True, exist_ok=True)
    Path(DATA_PATH).mkdir(parents=True, exist_ok=True)

    # 2. Set up DuckLake
    con = duckdb.connect()
    con.execute("INSTALL ducklake;")
    con.execute("LOAD ducklake;")
    con.execute(
        f"ATTACH 'ducklake:{CATALOG}' AS lake "
        f"(DATA_PATH '{DATA_PATH}', DATA_INLINING_ROW_LIMIT 0, AUTOMATIC_MIGRATION TRUE, OVERRIDE_DATA_PATH TRUE);"
    )
    con.execute("USE lake;")
    print(f"DuckLake attached  →  catalog={CATALOG}  data={DATA_PATH}/")

    # 3. Create table matching gold.trade_metrics
    con.execute("DROP TABLE IF EXISTS trade_metrics;")
    con.execute("""
        CREATE TABLE IF NOT EXISTS trade_metrics (
            product_id   VARCHAR,
            trade_hour   TIMESTAMP,
            total_volume DOUBLE,
            buy_volume   DOUBLE,
            sell_volume  DOUBLE,
            trade_count  BIGINT,
            high_price   DOUBLE,
            low_price    DOUBLE,
            avg_price    DOUBLE,
            price_open   DOUBLE,
            price_close  DOUBLE,
            buy_ratio    DOUBLE
        );
    """)
    print("Table ready: trade_metrics (12 columns)")

    # 4. Pull from PostgreSQL gold layer & load into DuckLake
    engine = get_pg_engine()
    print("\nReading from PostgreSQL analytics_gold.trade_metrics ...")
    df = read_gold_table(engine, "trade_metrics")
    engine.dispose()

    con.register("df", df)
    con.execute("DELETE FROM trade_metrics;")
    con.execute("INSERT INTO lake.trade_metrics SELECT * FROM df;")
    print(f"  trade_metrics → {len(df)} rows loaded")

    # 5. Spot-check the data
    print("\nSample: trade_metrics (latest 5 rows)")
    rows = con.execute("""
        SELECT product_id,
               trade_hour,
               ROUND(avg_price, 2)  AS avg_price,
               trade_count,
               ROUND(buy_ratio, 4)  AS buy_ratio,
               ROUND(price_open, 2) AS price_open,
               ROUND(price_close,2) AS price_close
        FROM trade_metrics
        ORDER BY trade_hour DESC
        LIMIT 5;
    """).fetchall()
    for r in rows:
        print(" ", r)

    # 6. Show snapshot history
    print_snapshots(con)

    # 7. Time travel demo
    snapshots = con.execute(
        "SELECT snapshot_id FROM ducklake_snapshots('lake') ORDER BY snapshot_id;"
    ).fetchall()

    if len(snapshots) >= 2:
        before_insert = snapshots[-2][0]
        print(f"\nTime travel: trade_metrics at VERSION {before_insert} (before last load)")
        try:
            rows_past = con.execute(f"""
                SELECT COUNT(*) AS row_count
                FROM trade_metrics AT (VERSION => {before_insert});
            """).fetchall()
            print("  row count at that snapshot:", rows_past[0][0])
        except Exception:
            print(f"  (snapshot {before_insert} predates table creation, skipping)")

    print("\nDone! Files written to:")
    print(f"  Metadata  →  {CATALOG}")
    print(f"  Parquet   →  {DATA_PATH}/")

if __name__ == "__main__":
    main()
