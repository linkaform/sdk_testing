# coding: utf-8

"""
Lista de la pestaña Vehículos de Bitácoras: get_list_bitacora con
desglose='vehiculos' (una fila por vehículo), opciones Dentro y Todos.
Notion: TB-095 y TB-096.
"""

import pytest

from .fixtures import *
from ..data.vehiculos_data import (
    LOCATION,
    AREA,
    LIMITE_LISTA,
    DESGLOSE_VEHICULOS,
    FILTRO_DENTRO,
    VEHICULO_VISITA,
)
from entradas_salidas.integration.helpers import ultima_visita, salida_silenciosa


@pytest.mark.integration
def test_vehiculos_dentro_solo_trae_visitas_abiertas(acceso_obj, pase_activo):
    """
    TB-095: Vehículos → Dentro debe traer solo vehículos de visitas abiertas
    (status Entrada), una fila por vehículo, e incluir el vehículo de la
    visita recién registrada. Si no, el guardia no ve qué vehículos siguen
    dentro de la ubicación.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"vehiculo": [VEHICULO_VISITA]})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con vehículo: {res}"

    try:
        visita = ultima_visita(acceso_obj, pase_activo)

        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO,
            desglose=DESGLOSE_VEHICULOS, limit=LIMITE_LISTA,
        )
        filas = dentro["records"]

        assert filas, "Vehículos Dentro viene vacío"
        assert all(r["status_visita"] == "Entrada" for r in filas), (
            f"Vehículos Dentro trae otros estatus: {sorted({r['status_visita'] for r in filas})}"
        )
        assert all(len(r["vehiculos"]) == 1 for r in filas), "Hay filas con más de un vehículo (no se desglosó)"

        filas_visita = [r for r in filas if r["_id"] == visita["_id"]]
        assert len(filas_visita) == 1, f"La visita debe ser una fila (un vehículo): {len(filas_visita)}"
        assert filas_visita[0]["vehiculos"][0]["placas"] == VEHICULO_VISITA["placas"]
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)


@pytest.mark.integration
def test_vehiculo_tras_la_salida_sale_de_dentro_y_sigue_en_todos(acceso_obj, pase_activo):
    """
    TB-096: después de registrar la salida, el vehículo de la visita ya no
    debe salir en Vehículos → Dentro, pero sí en Vehículos → Todos con status
    Salida. Si sigue en Dentro, el guardia cree que el vehículo no ha salido.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"vehiculo": [VEHICULO_VISITA]})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con vehículo: {res}"
    visita = ultima_visita(acceso_obj, pase_activo)

    try:
        acceso_obj.do_out(pase_activo, LOCATION, AREA)

        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO,
            desglose=DESGLOSE_VEHICULOS, limit=LIMITE_LISTA,
        )
        assert visita["_id"] not in {r["_id"] for r in dentro["records"]}, "El vehículo sigue en Dentro después de la salida"

        todos = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, desglose=DESGLOSE_VEHICULOS, limit=LIMITE_LISTA,
        )
        filas_visita = [r for r in todos["records"] if r["_id"] == visita["_id"]]
        assert len(filas_visita) == 1, f"El vehículo no aparece en Todos: {len(filas_visita)} filas"
        assert filas_visita[0]["status_visita"] == "Salida", f"En Todos quedó '{filas_visita[0]['status_visita']}'"
        assert filas_visita[0]["vehiculos"][0]["placas"] == VEHICULO_VISITA["placas"]
    finally:
        # Si do_out falló, cierra la visita para no dejarla abierta en preprod.
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)
