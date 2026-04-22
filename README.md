# Crypto Pipeline Analysis

A real-time cryptocurrency data pipeline that ingests live trade data from Coinbase and processes it through a modern data stack.

## Architecture

```
Coinbase WebSocket
        |
    RabbitMQ (Message Queue)
        |
   PostgreSQL (Data Warehouse)
        |
       dbt (Data Transformation)
        |
   +----+----+
   |         |
DuckLake  Metabase
(Lakehouse) (Visualization)
        
Airflow (Orchestration - hourly dbt runs)
```

## Data Layers (Medallion Architecture)

| Layer | Location | Description |
|-------|----------|-------------|
| Bronze | `bronze.raw_trades` | Raw trade data from Coinbase, no transformation |
| Silver | `analytics_silver.trades` | Cleaned and deduplicated trades |
| Gold | `analytics_gold.trade_metrics` | Hourly aggregated metrics per currency pair |

## Data Collected

Live trade data for three currency pairs:
- BTC-USD
- ETH-USD
- SOL-USD

Each record contains: trade_id, product_id, price, size, side (buy/sell), timestamp.

## Gold Layer Metrics

| Field | Description |
|-------|-------------|
| trade_hour | Hour of trading activity |
| total_volume | Total traded volume |
| buy_volume | Total buy volume |
| sell_volume | Total sell volume |
| trade_count | Number of trades |
| high_price | Highest trade price |
| low_price | Lowest trade price |
| avg_price | Average trade price |
| price_open | First trade price in the hour |
| price_close | Last trade price in the hour |
| buy_ratio | Buy volume / total volume |

## Tech Stack

- **Python** - Producer and consumer scripts
- **RabbitMQ** - Message queue between producer and consumer
- **PostgreSQL** - Data warehouse
- **dbt** - Data transformation and testing
- **Apache Airflow** - Hourly pipeline orchestration
- **DuckLake** - Local lakehouse with time travel capability
- **Metabase** - Data visualization
- **Docker** - Container orchestration

## Project Structure

```
crypto_pipeline_analysis/
├── crypto_pipeline/
│   └── scripts/
│       ├── producer.py       # Fetches data from Coinbase WebSocket
│       └── consumer.py       # Consumes from RabbitMQ, writes to PostgreSQL
├── dbt_project/
│   └── models/
│       ├── silver/
│       │   ├── trades.sql    # Deduplication and cleaning
│       │   ├── sources.yml   # Bronze source definition
│       │   └── schema.yml    # Data quality tests
│       └── gold/
│           ├── trade_metrics.sql  # Hourly aggregations
│           └── schema.yml         # Data quality tests
├── ducklake/
│   └── ducklake_export.py    # Exports gold layer to DuckLake
├── airflow/
│   └── dags/
│       └── dbt_hourly.py     # Hourly dbt DAG
├── sql/
│   └── init.sql              # Bronze schema initialization
└── docker-compose.yml        # All services
```

## Setup

**Prerequisites:** Docker, Python 3.12, pip

**1. Start infrastructure**
```bash
docker-compose up -d
```

**2. Create virtual environment**
```bash
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

**3. Start data ingestion**

Open two terminals:
```bash
# Terminal 1
python crypto_pipeline/scripts/consumer.py

# Terminal 2
python crypto_pipeline/scripts/producer.py
```

**4. Run dbt transformations**
```bash
cd dbt_project
dbt run --profiles-dir .
dbt test --profiles-dir .
```

**5. Export to DuckLake**
```bash
python ducklake/ducklake_export.py
```

**6. Access services**

| Service | URL |
|---------|-----|
| Metabase | http://localhost:3000 |
| Airflow | http://localhost:8080 |
| RabbitMQ Management | http://localhost:15672 |

## Data Quality

22 automated dbt tests covering:
- `not_null` checks on all key fields
- `unique` constraint on trade_id
- `accepted_values` for product_id and side fields
