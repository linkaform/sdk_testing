# coding: utf-8

"""
Script Log: buscar por nombre de script (list_script_logs en Sanic) con la
colección simulada.
Notion: TB-372.
"""

import pytest

from .helpers import script_logs_simulados
from ..data.logs_data import (
    NOMBRE_SCRIPT,
    IDS_CON_ESE_NOMBRE,
)

pytestmark = pytest.mark.back("sanic")


@pytest.mark.bug(1632)
def test_script_log_buscar_por_nombre_de_script_filtra_por_sus_ids(script_logs, mocker):
    """
    TB-372: al buscar un script por nombre, list_script_logs debe filtrar
    los logs solo por los scripts cuyo nombre contiene ese texto, sin
    importar mayúsculas. Si el filtro incluye otros scripts, la búsqueda
    regresa logs que no tienen nada que ver. Ticket 2611-1632: sin
    script_ids, list_script_logs mete todos los scripts visibles antes de
    sumar los que coinciden con el nombre.
    """
    logs = script_logs
    coleccion = script_logs_simulados(logs, mocker)

    logs.list_script_logs(script_name=NOMBRE_SCRIPT)

    match = coleccion.find.call_args.args[0]
    filtrados = set(match["script_id"]["$in"])
    assert filtrados == IDS_CON_ESE_NOMBRE, f"Filtra por los scripts {sorted(filtrados)}"
