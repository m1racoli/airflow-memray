import fnmatch
import functools
import json
import logging
import re
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, TypeVar, cast

import memray
from airflow.configuration import conf
from airflow.io.path import ObjectStoragePath
from airflow.models.taskinstancekey import TaskInstanceKey
from airflow.operators.python import get_current_context
from airflow.stats import Stats

logger = logging.getLogger(__name__)

C = TypeVar("C", bound=Callable)


def compile_memray_task_patterns() -> list[re.Pattern]:
    tasks = conf.get("memray", "tasks", fallback="")
    return [re.compile(fnmatch.translate(p)) for p in tasks.split(",")]


MEMRAY_TASK_PATTERNS: list[re.Pattern] = compile_memray_task_patterns()


def path_for_ti_key(ti_key: TaskInstanceKey) -> Path:
    base_folder = ObjectStoragePath(
        conf.get("memray", "base_folder", fallback="file:///tmp/airflow/memray"),
        conn_id=conf.get("memray", "storage_conn_id", fallback=None),
    )
    return base_folder / ti_key.dag_id / ti_key.task_id / ti_key.run_id / str(ti_key.try_number)


def make_flame_graph(folder: Path):
    import subprocess

    profile = folder / "profile.bin"
    result = folder / "flameGraph.html"

    try:
        subprocess.run(
            ["memray", "flamegraph", "-f", "--temporal", "-o", str(result), str(profile)],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Flame graph written to %s", result)
    except subprocess.CalledProcessError as err:
        for line in err.stderr.splitlines():
            logger.error(line)
        raise


def make_stats(folder: Path):
    import subprocess

    profile = folder / "profile.bin"
    result = folder / "stats.json"

    try:
        subprocess.run(
            ["memray", "stats", "-f", "--json", "-o", str(result), str(profile)],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Stats written to %s", result)
    except subprocess.CalledProcessError as err:
        for line in err.stderr.splitlines():
            logger.error(line)
        raise


def make_table(folder: Path):
    import subprocess

    profile = folder / "profile.bin"
    result = folder / "table.html"

    try:
        subprocess.run(
            ["memray", "table", "-f", "-o", str(result), str(profile)],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Table written to %s", result)
    except subprocess.CalledProcessError as err:
        for line in err.stderr.splitlines():
            logger.error(line)
        raise


def memray_func(f: C) -> C:

    @functools.wraps(f)
    def memray_execute(*args, **kwargs) -> Any:
        logger.info("::group::Memray pre task")

        tmp = TemporaryDirectory("memray")
        folder = Path(tmp.name)
        profile = folder / "profile.bin"
        destination = memray.FileDestination(profile, overwrite=True)

        logger.info("Writing profile to %s", profile)
        logger.info("Starting memray tracker")
        logger.info("::endgroup::")
        try:
            with memray.Tracker(destination=destination, native_traces=False):
                return f(*args, **kwargs)
        finally:
            logger.info("::group::Memray post task")
            try:
                post_task(folder)
            except Exception as e:
                logger.error("Error in post task: %s", e)
            logger.info("::endgroup::")

    return cast(C, memray_execute)


def post_task(folder: Path):
    logger.info("Memray tracker finished")
    make_flame_graph(folder)
    make_stats(folder)
    make_table(folder)

    context = get_current_context()
    ti = context["ti"]
    dst_folder = path_for_ti_key(ti.key)
    dst_folder.mkdir(parents=True, exist_ok=True)

    for file in ObjectStoragePath(folder).iterdir():
        file.copy(dst_folder / file.name)
        logger.info("%s copied to %s", file.name, dst_folder)

    with open(folder / "stats.json") as file:
        stats = json.load(file)

    for metric in ["total_allocations", "total_frames", "peak_memory"]:
        Stats.gauge(
            f"ti_memray_{metric}",
            value=stats["metadata"][metric],
            tags=ti.stats_tags,
        )
    logger.info("Memray stats submitted")


def get_url(filename: str, ti_key: TaskInstanceKey) -> str:
    import urllib.parse

    from flask import request

    url = request.host_url + "memray/" + filename + "?"
    params = {
        "dag_id": ti_key.dag_id,
        "task_id": ti_key.task_id,
        "run_id": ti_key.run_id,
        "try_number": ti_key.try_number,
        "map_index": ti_key.map_index,
    }
    return url + urllib.parse.urlencode(params)


def get_link(filename: str, ti_key: TaskInstanceKey) -> str:
    if ti_key.try_number > 1:
        ti_key = ti_key.with_try_number(ti_key.try_number - 1)

    folder = path_for_ti_key(ti_key)
    file = folder / filename

    if file.exists():
        logger.debug("File %s for %s exists", file, ti_key)
        return get_url(filename, ti_key)

    logger.debug("File %s for %s not found", file, ti_key)
    return ""


def ti_key_from_request() -> TaskInstanceKey:
    from flask import request

    args = request.args

    return TaskInstanceKey(
        dag_id=args["dag_id"],
        task_id=args["task_id"],
        run_id=args["run_id"],
        try_number=int(args["try_number"]),
        map_index=int(args["map_index"]),
    )


def send_ti_file(filename: str, mimetype: str = "text/html"):
    from flask import send_file

    ti_key = ti_key_from_request()
    folder = path_for_ti_key(ti_key)
    file = folder / filename

    f = file.open("rb")
    return send_file(f, mimetype=mimetype)
