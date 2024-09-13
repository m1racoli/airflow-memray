import logging

from airflow.models import BaseOperator, BaseOperatorLink
from airflow.models.taskinstancekey import TaskInstanceKey
from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint

logger = logging.getLogger(__name__)


blueprint = Blueprint(
    name="memray",
    import_name=__name__,
    url_prefix="/memray",
)


@blueprint.get("/flameGraph.html")
def flame_graph():
    from airflow_memray.core import send_ti_file

    return send_ti_file("flameGraph.html")


@blueprint.get("/stats.json")
def stats():
    from airflow_memray.core import send_ti_file

    return send_ti_file("stats.json", mimetype="application/json")


@blueprint.get("/table.html")
def table():
    from airflow_memray.core import send_ti_file

    return send_ti_file("table.html")


class MemrayFlameGraphLink(BaseOperatorLink):
    name = "Memray Flame Graph"

    def get_link(self, operator: BaseOperator, *, ti_key: TaskInstanceKey) -> str:
        from airflow_memray.core import get_link

        return get_link("flameGraph.html", ti_key)


class MemrayStatsLink(BaseOperatorLink):
    name = "Memray Stats"

    def get_link(self, operator: BaseOperator, *, ti_key: TaskInstanceKey) -> str:
        from airflow_memray.core import get_link

        return get_link("stats.json", ti_key)


class MemrayTableLink(BaseOperatorLink):
    name = "Memray Table"

    def get_link(self, operator: BaseOperator, *, ti_key: TaskInstanceKey) -> str:
        from airflow_memray.core import get_link

        return get_link("table.html", ti_key)


class MemrayPlugin(AirflowPlugin):
    name = "memray_plugin"

    flask_blueprints = [blueprint]
    global_operator_extra_links = [
        MemrayFlameGraphLink(),
        MemrayStatsLink(),
        MemrayTableLink(),
    ]
