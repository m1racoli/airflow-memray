__version__ = "0.0.0"


def get_provider_info():
    return {
        "package-name": "airflow-memray",
        "name": "Memray",
        "description": "Memory profiling for Airflow with `Memray <https://bloomberg.github.io/memray/>`__.",
        "versions": [__version__],
    }
