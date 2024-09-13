from time import sleep

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

SIZE = 512


def run() -> int:
    import numpy

    sleep(1)
    a = numpy.full([SIZE, SIZE, SIZE], 1)
    s = numpy.sum(a)
    a = None
    sleep(1)
    return int(s)


@task
def empty():
    # This task should not run with memray.
    pass


@task
def memray() -> int:
    return run()


@dag(
    schedule=None,
    start_date=days_ago(1),
)
def memray_demo():
    empty()

    EmptyOperator(
        task_id="empty_classic",
    )

    memray()

    PythonOperator(
        task_id="memray_classic",
        python_callable=run,
    )


memray_demo()
