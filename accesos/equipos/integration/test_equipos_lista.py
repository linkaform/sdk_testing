# coding: utf-8

"""
Lista de la pestaña Equipos de Bitácoras: get_list_bitacora con
desglose='equipos' (una fila por equipo), opciones Dentro y Todos.
Notion: TB-101 a TB-103.
"""

import pytest

from .fixtures import *
from ..data.equipos_data import (
    LOCATION,
    AREA,
    LIMITE_LISTA,
    DESGLOSE_EQUIPOS,
    FILTRO_DENTRO,
    EQUIPO_VISITA,
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
