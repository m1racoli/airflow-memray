# Airflow Memray

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![code style: black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![image](https://img.shields.io/pypi/v/airflow-memray.svg)](https://pypi.python.org/pypi/airflow-memray)
[![image](https://img.shields.io/pypi/l/airflow-memray.svg)](https://github.com/m1racoli/airflow-memray/blob/main/LICENSE)
[![image](https://img.shields.io/pypi/pyversions/airflow-memray.svg)](https://pypi.python.org/pypi/airflow-memray)

Memory profiling for Airflow with [Memray](https://bloomberg.github.io/memray/).

## Configuration Reference

This section contains the list of all the available Airflow Memray configurations that you can set in `airflow.cfg` file or using environment variables.

### base_folder

The base folder under which Airflow Memray will store profiling results. Possible values can be anything what is supported by [Airflow Object Storage](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/objectstorage.html).

If it refers to a local file system path, then it must be accessible by the task and the webserver.

**Default**: `"file:///tmp/airflow/memray"`

**Environment Variable**: `AIRFLOW__MEMRAY__BASE_FOLDER`

### storage_conn_id

The Airflow Connection to use if [base_folder](#base_folder) is set to a remote cloud storage location.

**Default**: `None`

**Environment Variable**: `AIRFLOW__MEMRAY__STORAGE_CONN_ID`

### tasks

The tasks to be profiled as a comma separated list of wildcard pattern as implemented by the [fnmatch](https://docs.python.org/3/library/fnmatch.html) module. The pattern are applied against the full task ID in the form `<dag_id>.<task_id>`.

Set it to `"*"` to profile all tasks.

**Default**: `""`

**Environment Variable**: `AIRFLOW__MEMRAY__TASKS`

## Airflow Summit 2024

I have given a presentation about this package at Airflow Summit 2024.

You can visit the [official page of the presentation](https://airflowsummit.org/sessions/2024/profiling-airflow-tasks-with-memray/) or directly watch video on YouTube by clicking on the following picture:

[![Profiling Airflow tasks with Memray](https://img.youtube.com/vi/QHLedv-j8Hc/0.jpg)](https://www.youtube.com/watch?v=QHLedv-j8Hc)
