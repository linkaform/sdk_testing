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
    URL_LOG,
    LOGS_CON_Y_SIN_ARCHIVO,
    URL_OTRO_HOST,
    URL_SIN_HTTPS,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["_ids_by_name", "_to_date", "get_script_log_content", "list_script_logs"]


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


@pytest.mark.unit
@pytest.mark.target("list_script_logs")
def test_script_log_solo_los_logs_con_archivo_traen_liga(script_logs, mocker):
    """
    TB-374: el botón para ver el log solo debe aparecer cuando el log tiene
    archivo (el traceback es la URL). Si el traceback es el texto de un
    error, no hay archivo que abrir y no debe traer liga.
    """
    logs = script_logs
    script_logs_simulados(logs, mocker, registros=LOGS_CON_Y_SIN_ARCHIVO)

    con_archivo, sin_archivo = logs.list_script_logs()["records"]

    assert (con_archivo["has_log"], con_archivo["log_url"]) == (True, URL_LOG)
    assert (sin_archivo["has_log"], sin_archivo["log_url"]) == (False, "")


@pytest.mark.unit
@pytest.mark.target("get_script_log_content")
def test_script_log_no_se_descarga_un_log_de_una_url_que_no_es_de_backblaze(script_logs, mocker):
    """
    TB-375: el contenido del log lo descarga el servidor, así que
    get_script_log_content solo debe aceptar URLs https de Backblaze. Con otro
    host o sin https responde "URL de log no valida" sin descargar nada; si
    no, cualquiera podría usar la ruta para que el servidor pida otras URLs.
    """
    logs = script_logs
    descargar = mocker.patch("requests.get")

    assert logs.get_script_log_content(URL_OTRO_HOST) == {"error": "URL de log no valida"}
    assert logs.get_script_log_content(URL_SIN_HTTPS) == {"error": "URL de log no valida"}

    descargar.assert_not_called()
