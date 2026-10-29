# coding: utf-8

"""
Etapas de un camión en el patio (save_bitac_transportista_record): lo que
hace el botón de avanzar etapa en el detalle del transportista.
Notion: TB-089.
"""

from datetime import datetime

import pytest
import pytz

from .fixtures import *
from ..data.control_patio_data import (
    ETAPAS_HASTA_TERMINADO,
    ESTATUS_CARGA_DESCARGA,
    ESTATUS_TERMINADO,
)


@pytest.mark.integration
def test_avanzar_etapas_hasta_terminado_llena_fechas(patio_obj, camion_en_arribo):
    """
    TB-089: avanzar de 'arribo' hasta 'terminado' debe guardar cada etapa, la
    fecha de descarga al entrar a carga/descarga y la fecha de terminado al
    final. Sin esas fechas no se sabe cuánto tardó el camión en el andén.
    """
    record_id = camion_en_arribo
    anden = patio_obj.get_andenes()[0]
    hoy = datetime.now(pytz.timezone(patio_obj.user["timezone"])).strftime("%Y-%m-%d")

    for estatus in ETAPAS_HASTA_TERMINADO:
        # Igual que cambiarEstatus del front: en carga/descarga se manda el andén elegido.
        data = {"estatus": estatus, "anden": anden} if estatus == ESTATUS_CARGA_DESCARGA else {"estatus": estatus}
        patio_obj.save_bitac_transportista_record(record_id, data)

        registro = patio_obj.get_bitac_transportista_record(record_id)
        assert registro.get("estatus") == estatus, f"Al avanzar a '{estatus}' quedó en '{registro.get('estatus')}'"

        if estatus == ESTATUS_CARGA_DESCARGA:
            fecha_descarga = registro.get("fecha_hora_descarga") or ""
            assert fecha_descarga.startswith(hoy), f"No se guardó la fecha de descarga: {fecha_descarga!r}"
            assert registro.get("anden_asignado") == anden, f"No se guardó el andén: {registro.get('anden_asignado')}"

    assert registro.get("fecha_hora_descarga") == fecha_descarga, "La fecha de descarga cambió al terminar"
    assert (registro.get("fecha_hora_terminado") or "").startswith(hoy), (
        f"No se guardó la fecha de terminado: {registro.get('fecha_hora_terminado')!r}"
    )
