# coding: utf-8

"""
Llegada de un camión al patio (create_visit_transportista): lo que registra
el guardia en "Nuevo Acceso Transportista".
Notion: TB-087 y TB-088.
"""

import copy
from datetime import datetime

import pytest
import pytz

from .fixtures import *
from ..data.control_patio_data import (
    LLEGADA_SIN_PASE,
    ESTATUS_ARRIBO,
    ESTATUS_DESCARTADO,
    ESTATUS_PROGRAMADO,
    PASE_COMPLETADO,
)


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


@pytest.mark.integration
def test_llegada_con_pase_reutiliza_el_registro_programado(patio_obj, mock_pase_transportista):
    """
    TB-088: al crear un pase de transportista queda un registro 'programado'
    en el patio. "Registrar llegada de pase" debe pasar ese mismo registro a
    'arribo' (no crear otro), conservar el andén del pase y marcar el pase
    como completado. Si duplica, el camión aparece dos veces en el Kanban.
    """
    res_pase = patio_obj.create_pass_transportista(mock_pase_transportista)
    pase_id = (res_pase.get("json") or {}).get("id")
    assert pase_id, f"No se creó el pase de transportista: {res_pase}"

    pase = patio_obj.get_pass_transportista(record_id=pase_id)
    programado_id = pase.get("bitacora_id")
    assert programado_id, f"El pase no dejó registro programado en el patio: {pase}"
    assert patio_obj.get_bitac_transportista_record(programado_id).get("estatus") == ESTATUS_PROGRAMADO

    llegada = copy.deepcopy(LLEGADA_SIN_PASE)
    llegada["num_de_pase"] = pase_id
    res = patio_obj.create_visit_transportista(llegada)
    record_id = (res.get("json") or {}).get("id") or res.get("id")

    try:
        assert record_id == programado_id, f"La llegada creó otro registro ({record_id}) en vez de usar {programado_id}"

        registro = patio_obj.get_bitac_transportista_record(programado_id)
        anden = mock_pase_transportista["lugar_entrega_recepcion"]["anden"]
        assert registro.get("estatus") == ESTATUS_ARRIBO, f"El camión quedó en '{registro.get('estatus')}'"
        assert registro.get("anden_asignado") == anden, f"Se perdió el andén del pase: {registro.get('anden_asignado')}"

        estado_pase = patio_obj.get_pass_transportista(record_id=pase_id).get("estado_transportista")
        assert estado_pase == PASE_COMPLETADO, f"El pase quedó '{estado_pase}'"
    finally:
        for rid in {programado_id, record_id} - {None}:
            patio_obj.save_bitac_transportista_record(rid, {"estatus": ESTATUS_DESCARTADO})
