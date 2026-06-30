from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'shoppulse',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    'shoppulse_end_to_end_pipeline',
    default_args=default_args,
    description='Orchestrates dbt tasks for shoppulse',
    schedule_interval='@hourly',
    catchup=False
) as dag:

    # Health check task to ensure the database is reachable
    health_check = PostgresOperator(
        task_id='health_check',
        postgres_conn_id='postgres_default',
        sql='SELECT 1;'
        
    )

    # Run transformations task to execute dbt models
    run_dbt_transformations = BashOperator(
        task_id='run_dbt_transformations',
        bash_command='cd /opt/airflow/dbt/shoppulse && dbt build --profiles-dir .',
    )

    # Define task dependencies
    health_check >> run_dbt_transformations