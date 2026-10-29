# coding: utf-8

"""
Llegada de un camión al patio (create_visit_transportista): lo que registra
el guardia en "Nuevo Acceso Transportista".
Notion: TB-087.
"""

from datetime import datetime

import pytest
import pytz

from .fixtures import *
from ..data.control_patio_data import LLEGADA_SIN_PASE, ESTATUS_ARRIBO, ESTATUS_DESCARTADO


@pytest.mark.integration
def test_llegada_sin_pase_crea_camion_en_arribo(patio_obj):
    """
    TB-087: registrar la llegada de un camión sin pase debe crear un registro
    nuevo en la bitácora de transportistas en 'arribo', con la fecha de
    ingreso de hoy y los datos del vehículo enviados. Si no, el camión no
    aparece en la columna de Arribo del patio.
    """
    res = patio_obj.create_visit_transportista(LLEGADA_SIN_PASE)
    record_id = (res.get("json") or {}).get("id")
    assert record_id, f"No se creó el registro del camión: {res}"

    try:
        registro = patio_obj.get_bitac_transportista_record(record_id)
        hoy = datetime.now(pytz.timezone(patio_obj.user["timezone"])).strftime("%Y-%m-%d")
        vehiculo = LLEGADA_SIN_PASE["vehiculo"]

        assert registro.get("estatus") == ESTATUS_ARRIBO, f"El camión quedó en '{registro.get('estatus')}'"
        assert (registro.get("fecha_hora_ingreso") or "").startswith(hoy), (
            f"Fecha de ingreso inesperada: {registro.get('fecha_hora_ingreso')}"
        )
        assert not registro.get("num_de_pase"), f"Un camión sin pase quedó con pase: {registro.get('num_de_pase')}"
        assert registro.get("placas_de_vehiculo") == vehiculo["placa"]
        assert registro.get("empresa_transportista") == vehiculo["transportista"]
        assert registro.get("procedencia") == vehiculo["procedencia"]
    finally:
        # Lo saca del patio de preprod (botón X del Kanban).
        patio_obj.save_bitac_transportista_record(record_id, {"estatus": ESTATUS_DESCARTADO})
