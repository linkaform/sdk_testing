# coding: utf-8

"""Logs: Script Log (list_script_logs y get_script_log_content) y Workflow Log,
sin tocar la cuenta.
Notion: TB-371 a TB-380.

Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS:
./lkf test corre este archivo cuando cambia alguna funcion de C10_TRIGGERS.
La seccion solo existe en Sanic: los tests llevan back("sanic") y en addons
salen SKIPPED.
"""

import pytest

from ..data.logs_data import (
    SCRIPTS_VISIBLES,
    USUARIOS_CUENTA,
    FECHA_INICIO,
    FECHA_FIN,
    DESDE,
    HASTA,
    NOMBRE_SCRIPT,
    IDS_CON_ESE_NOMBRE,
    LOGS_GUARDADOS,
    LOGS_POR_PAGINA,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["_ids_by_name", "_to_date", "list_script_logs"]


def script_logs_simulados(logs, mocker, registros=()):
    """Simula los nombres que resuelve _name_maps y la colección script_log;
    regresa el mock de la colección para revisar la consulta."""
    mocker.patch.object(logs, "_name_maps", return_value={"users": dict(USUARIOS_CUENTA), "scripts": dict(SCRIPTS_VISIBLES)})
    coleccion = mocker.MagicMock()
    coleccion.find.return_value.sort.return_value.skip.return_value.limit.return_value = list(registros)
    mocker.patch.object(type(logs), "script_log_cr", new_callable=mocker.PropertyMock, return_value=coleccion)
    return coleccion


@pytest.mark.unit
@pytest.mark.target("list_script_logs", "_to_date")
def test_script_log_el_filtro_de_fechas_toma_el_dia_completo(script_logs, mocker):
    """
    TB-371: el filtro de fechas del Script Log manda solo el día
    (YYYY-MM-DD). list_script_logs debe consultar desde el inicio del primer
    día hasta el último milisegundo del día final; si cortara a las 00:00 del
    día final, los logs de ese día no saldrían.
    """
    logs = script_logs
    coleccion = script_logs_simulados(logs, mocker)

    logs.list_script_logs(date1=FECHA_INICIO, date2=FECHA_FIN)

    match = coleccion.find.call_args.args[0]
    assert match["start_date"] == {"$gte": DESDE, "$lte": HASTA}


@pytest.mark.unit
@pytest.mark.target("list_script_logs", "_ids_by_name")
def test_script_log_buscar_por_nombre_de_script_filtra_por_sus_ids(script_logs, mocker):
    """
    TB-372: al buscar un script por nombre, list_script_logs debe filtrar
    los logs solo por los scripts cuyo nombre contiene ese texto, sin
    importar mayúsculas. Si el filtro incluye otros scripts, la búsqueda
    regresa logs que no tienen nada que ver.
    """
    logs = script_logs
    coleccion = script_logs_simulados(logs, mocker)

    logs.list_script_logs(script_name=NOMBRE_SCRIPT)

    match = coleccion.find.call_args.args[0]
    filtrados = set(match["script_id"]["$in"])
    assert filtrados == IDS_CON_ESE_NOMBRE, f"Filtra por los scripts {sorted(filtrados)}"


@pytest.mark.unit
@pytest.mark.target("list_script_logs")
def test_script_log_la_lista_sabe_si_hay_pagina_siguiente_sin_contar_todos_los_logs(script_logs, mocker):
    """
    TB-373: la colección de logs tiene millones de registros, así que la
    lista no los cuenta: pide una fila de más y con ella sabe si hay página
    siguiente. Esa fila extra no se muestra.
    """
    logs = script_logs
    coleccion = script_logs_simulados(logs, mocker, registros=LOGS_GUARDADOS)

    res = logs.list_script_logs(limit=LOGS_POR_PAGINA)

    coleccion.find.return_value.sort.return_value.skip.return_value.limit.assert_called_once_with(LOGS_POR_PAGINA + 1)
    coleccion.count_documents.assert_not_called()
    assert res["has_next"] is True
    assert res["records_on_page"] == LOGS_POR_PAGINA
    assert [r["id"] for r in res["records"]] == [r["_id"] for r in LOGS_GUARDADOS[:LOGS_POR_PAGINA]]
