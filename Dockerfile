FROM quay.io/astronomer/astro-runtime:11.10.1-base

USER root
WORKDIR /usr/local/airflow

COPY requirements.txt pyproject.toml ./
COPY airflow_memray/__init__.py airflow_memray/
RUN pip install --no-cache-dir -r requirements.txt

ENV AIRFLOW__SCHEDULER__CATCHUP_BY_DEFAULT=false \
    AIRFLOW__METRICS__STATSD_ON=True \
    AIRFLOW__METRICS__STATSD_HOST=statsd-exporter \
    AIRFLOW__MEMRAY__BASE_FOLDER=file://tests/memray \
    AIRFLOW__MEMRAY__TASKS=memray_demo.memray*

COPY --chown=astro:astro . ./

USER astro
