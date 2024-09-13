import logging

from airflow.decorators.base import DecoratedOperator
from airflow.models import BaseOperator
from airflow.policies import hookimpl

from airflow_memray.core import MEMRAY_TASK_PATTERNS, memray_func

logger = logging.getLogger(__name__)


@hookimpl
def task_policy(task: BaseOperator) -> None:
    full_id = f"{task.dag_id}.{task.task_id}"
    if all(p.match(full_id) is None for p in MEMRAY_TASK_PATTERNS):
        return

    if isinstance(task, DecoratedOperator):
        task.python_callable = memray_func(task.python_callable)
    else:
        task.execute = memray_func(task.execute)  # type: ignore

    logger.debug("memray enabled for %s", task)
