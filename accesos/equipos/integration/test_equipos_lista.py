# coding: utf-8

"""
Lista de la pestaña Equipos de Bitácoras: get_list_bitacora con
desglose='equipos' (una fila por equipo), opciones Dentro y Todos.
Notion: TB-101 a TB-103.
"""

from math import ceil

import pytest

from .fixtures import *
from ..data.equipos_data import (
    LOCATION,
    AREA,
    LIMITE_LISTA,
    DESGLOSE_EQUIPOS,
    FILTRO_DENTRO,
    EQUIPO_VISITA,
    EQUIPOS_VISITA_DOS,
    FILAS_POR_PAGINA,
)
from entradas_salidas.integration.helpers import ultima_visita, salida_silenciosa


@pytest.mark.integration
def test_equipos_dentro_solo_trae_visitas_abiertas(acceso_obj, pase_activo):
    """
    TB-101: Equipos → Dentro debe traer solo equipos de visitas abiertas
    (status Entrada), una fila por equipo, e incluir el equipo de la visita
    recién registrada. Si no, el guardia no ve qué equipos siguen dentro de
    la ubicación.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"equipo": [EQUIPO_VISITA]})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con equipo: {res}"

    try:
        visita = ultima_visita(acceso_obj, pase_activo)

        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO,
            desglose=DESGLOSE_EQUIPOS, limit=LIMITE_LISTA,
        )
        filas = dentro["records"]

        assert filas, "Equipos Dentro viene vacío"
        assert all(r["status_visita"] == "Entrada" for r in filas), (
            f"Equipos Dentro trae otros estatus: {sorted({r['status_visita'] for r in filas})}"
        )
        assert all(len(r["equipos"]) == 1 for r in filas), "Hay filas con más de un equipo (no se desglosó)"

        filas_visita = [r for r in filas if r["_id"] == visita["_id"]]
        assert len(filas_visita) == 1, f"La visita debe ser una fila (un equipo): {len(filas_visita)}"
        assert filas_visita[0]["equipos"][0]["numero_serie"] == EQUIPO_VISITA["serie"]
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)


@pytest.mark.integration
def test_equipo_tras_la_salida_sale_de_dentro_y_sigue_en_todos(acceso_obj, pase_activo):
    """
    TB-102: después de registrar la salida, el equipo de la visita ya no debe
    salir en Equipos → Dentro, pero sí en Equipos → Todos con status Salida.
    Si sigue en Dentro, el guardia cree que el equipo no ha salido.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"equipo": [EQUIPO_VISITA]})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con equipo: {res}"
    visita = ultima_visita(acceso_obj, pase_activo)

    try:
        acceso_obj.do_out(pase_activo, LOCATION, AREA)

        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO,
            desglose=DESGLOSE_EQUIPOS, limit=LIMITE_LISTA,
        )
        assert visita["_id"] not in {r["_id"] for r in dentro["records"]}, "El equipo sigue en Dentro después de la salida"

        todos = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, desglose=DESGLOSE_EQUIPOS, limit=LIMITE_LISTA,
        )
        filas_visita = [r for r in todos["records"] if r["_id"] == visita["_id"]]
        assert len(filas_visita) == 1, f"El equipo no aparece en Todos: {len(filas_visita)} filas"
        assert filas_visita[0]["status_visita"] == "Salida", f"En Todos quedó '{filas_visita[0]['status_visita']}'"
        assert filas_visita[0]["equipos"][0]["numero_serie"] == EQUIPO_VISITA["serie"]
    finally:
        # Si do_out falló, cierra la visita para no dejarla abierta en preprod.
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)


@pytest.mark.integration
def test_paginacion_de_equipos_no_repite_ni_pierde(acceso_obj, pase_activo):
    """
    TB-103: con el desglose, la paginación cuenta filas de equipo. Al recorrer
    de una fila por página, los 2 equipos de una visita deben salir una vez
    cada uno, y total_pages/actual_page deben cuadrar con el total. Si se
    repite o se pierde un equipo al cambiar de página, el guardia no ve todos
    los equipos que entraron.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"equipo": EQUIPOS_VISITA_DOS})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con equipos: {res}"

    try:
        visita = ultima_visita(acceso_obj, pase_activo)
        # El folio no es único en preprod: se revisan solo las filas de esta visita.
        por_folio = [{"key": "folio", "values": [visita["folio"]], "exact": True}]

        primera = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, facets=por_folio,
            desglose=DESGLOSE_EQUIPOS, limit=FILAS_POR_PAGINA, offset=0,
        )
        total = primera["total_records"]
        assert primera["total_pages"] == ceil(total / FILAS_POR_PAGINA)

        filas = []
        for pagina in range(primera["total_pages"]):
            res_pagina = acceso_obj.get_list_bitacora(
                location=LOCATION, area=AREA, facets=por_folio,
                desglose=DESGLOSE_EQUIPOS, limit=FILAS_POR_PAGINA, offset=pagina * FILAS_POR_PAGINA,
            )
            assert res_pagina["actual_page"] == pagina + 1, f"Página {pagina + 1} reporta {res_pagina['actual_page']}"
            assert res_pagina["records_on_page"] == len(res_pagina["records"]) <= FILAS_POR_PAGINA
            filas.extend(res_pagina["records"])

        assert len(filas) == total, f"Recorriendo las páginas salen {len(filas)} filas y el total dice {total}"
        series_visita = [r["equipos"][0]["numero_serie"] for r in filas if r["_id"] == visita["_id"]]
        assert sorted(series_visita) == sorted(e["serie"] for e in EQUIPOS_VISITA_DOS), (
            f"Equipos de la visita al recorrer las páginas: {series_visita}"
        )
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)
