from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'lucas', 
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ml_smartphones_pipeline',
    default_args=default_args,
    description='Pipeline ELT Mercado Livre',
    schedule_interval='@hourly',
    catchup=False,
    tags=['ecommerce', 'mercadolivre'],
) as dag:

    run_producer = BashOperator(
        task_id='collect_products',
        bash_command='python /opt/airflow/collector/kafka_producer.py',
    )

    run_consumer = BashOperator(
        task_id='consume_to_postgres',
        bash_command='python /opt/airflow/collector/kafka_consumer.py',
    )

    run_dbt = BashOperator(
        task_id='run_dbt_models',
        bash_command='cd /opt/airflow/dbt && dbt clean && dbt run --profiles-dir .',
    )

    run_producer >> run_consumer >> run_dbt