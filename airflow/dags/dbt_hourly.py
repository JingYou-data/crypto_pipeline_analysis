from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id='dbt_hourly_refresh',
    start_date=datetime(2026, 4, 21),
    schedule_interval='@hourly',
    catchup=False,
) as dag:

    task_silver = BashOperator(
        task_id='run_dbt_silver',
        bash_command='cd /opt/airflow/dbt_project && dbt run --profiles-dir . --target docker --select silver.trades',
    )

    task_gold = BashOperator(
        task_id='run_dbt_gold',
        bash_command='cd /opt/airflow/dbt_project && dbt run --profiles-dir . --target docker --select gold.trade_metrics',
    )

    task_silver >> task_gold
