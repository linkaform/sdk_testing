# coding: utf-8

"""
Vehículos Dentro en la app: list_bitacora2 sin desglose y con
prioridades=['entrada'] (la app desglosa los vehículos en el celular).
Notion: TB-100.
"""

import pytest

from .fixtures import *
from ..data.vehiculos_data import (
    LOCATION,
    AREA,
    LIMITE_LISTA,
    PRIORIDADES_APP_DENTRO,
    VEHICULO_APP,
)
from entradas_salidas.integration.helpers import ultima_visita, salida_silenciosa


@pytest.mark.integration
def test_vehiculos_dentro_en_la_app_solo_trae_visitas_abiertas(acceso_obj, pase_activo):
    """
    TB-100: la lista que pide la app para Vehículos Dentro debe traer solo
    visitas en Entrada e incluir la visita con vehículo recién registrada,
    con su placa. Si no, el guardia en el celular no ve qué vehículos
    siguen dentro.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"vehiculo": [VEHICULO_APP]})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con vehículo: {res}"

    try:
        visita = ultima_visita(acceso_obj, pase_activo)

        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, prioridades=PRIORIDADES_APP_DENTRO, limit=LIMITE_LISTA,
        )
        registros = dentro["records"]

        assert registros, "Vehículos Dentro de la app viene vacío"
        assert all(r["status_visita"] == "Entrada" for r in registros), (
            f"La lista de la app trae otros estatus: {sorted({r['status_visita'] for r in registros})}"
        )

        registros_visita = [r for r in registros if r["_id"] == visita["_id"]]
        assert len(registros_visita) == 1, f"La visita debe salir una vez (sin desglose): {len(registros_visita)}"
        placas = [v["placas"] for v in registros_visita[0]["vehiculos"]]
        assert placas == [VEHICULO_APP["placas"]], f"Vehículos de la visita en la app: {placas}"
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)
