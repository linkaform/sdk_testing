# coding: utf-8

"""
Lista del patio (get_bitac_transportista_records): lo que pinta el Kanban de
Control de patio y la app, con rango de fechas y filtros del panel.
Notion: TB-093.
"""

from datetime import datetime

import pytest
import pytz

from .fixtures import *
from ..data.control_patio_data import LLEGADA_SIN_PASE, ESTATUS_ARRIBO


@pytest.mark.integration
def test_lista_patio_respeta_rango_de_fechas_y_filtros(patio_obj, camion_en_arribo):
    """
    TB-093: con el rango de hoy y los filtros de estatus y tipo de vehículo,
    la lista debe traer solo camiones de hoy con ese estatus y tipo, e incluir
    el camión recién llegado. Si los filtros no se aplican, el guardia ve
    camiones de otros días o etapas en la columna equivocada.
    """
    record_id = camion_en_arribo
    hoy = datetime.now(pytz.timezone(patio_obj.user["timezone"])).strftime("%Y-%m-%d")
    tipo = LLEGADA_SIN_PASE["vehiculo"]["tipo_vehiculo"]

    patio = patio_obj.get_bitac_transportista_records(
        date_from=hoy, date_to=hoy, estatus=[ESTATUS_ARRIBO], tipo_de_vehiculo=[tipo]
    )

    assert patio, "La lista del patio de hoy viene vacía"
    assert record_id in {r.get("_id") for r in patio}, "El camión recién llegado no aparece en la lista"
    assert all(r.get("estatus") == ESTATUS_ARRIBO for r in patio), (
        f"La lista trae otros estatus: {sorted({r.get('estatus') for r in patio})}"
    )
    assert all((r.get("fecha_hora_ingreso") or "").startswith(hoy) for r in patio), (
        f"La lista trae camiones de otros días: {sorted({(r.get('fecha_hora_ingreso') or '')[:10] for r in patio})}"
    )
    assert all(r.get("tipo_de_vehiculo") == tipo for r in patio), (
        f"La lista trae otros tipos de vehículo: {sorted({r.get('tipo_de_vehiculo') for r in patio})}"
    )
