import logging

from airflow.models.taskinstance import TaskInstance
from airflow.policies import hookimpl

from airflow_memray.core import MEMRAY_TASK_PATTERNS, memray_func

logger = logging.getLogger(__name__)


MEMRAY_ENABLED_KEY = "_memray_enabled"


@hookimpl
def task_instance_mutation_hook(task_instance: TaskInstance) -> None:
    full_id = f"{task_instance.dag_id}.{task_instance.task_id}"
    if all(p.match(full_id) is None for p in MEMRAY_TASK_PATTERNS):
        return

    task = task_instance.task

    # somehow this hook can get called multiple times
    # making sure we don't wrap the function multiple times
    if getattr(task.__class__, MEMRAY_ENABLED_KEY, False):
        return

    exec_function = "execute"
    original_execute = getattr(task.__class__, exec_function)
    setattr(task.__class__, exec_function, memray_func(original_execute))
    setattr(task.__class__, MEMRAY_ENABLED_KEY, True)

    logger.info("memray enabled for %s", task_instance)
