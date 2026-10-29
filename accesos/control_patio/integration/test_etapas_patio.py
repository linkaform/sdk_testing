# coding: utf-8

"""
Etapas de un camión en el patio (save_bitac_transportista_record): lo que
hace el botón de avanzar etapa en el detalle del transportista.
Notion: TB-089 a TB-092.
"""

from datetime import datetime

import pytest
import pytz

from .fixtures import *
from ..data.control_patio_data import (
    ETAPAS_HASTA_TERMINADO,
    ESTATUS_CARGA_DESCARGA,
    ESTATUS_TERMINADO,
    ESTATUS_DESCARTADO,
    ESTATUS_COLUMNAS_KANBAN,
    LLEGADA_SIN_PASE,
    EMBARQUE_EDITADO,
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


@pytest.mark.integration
def test_descartar_camion_lo_saca_del_patio(patio_obj, camion_en_arribo):
    """
    TB-090: el botón X del Kanban descarta el camión. Debe quedar en
    'descartado' y ya no salir en las columnas del patio de hoy; si sigue
    saliendo, el guardia ve camiones que ya no están.
    """
    record_id = camion_en_arribo
    hoy = datetime.now(pytz.timezone(patio_obj.user["timezone"])).strftime("%Y-%m-%d")

    patio_obj.save_bitac_transportista_record(record_id, {"estatus": ESTATUS_DESCARTADO})

    registro = patio_obj.get_bitac_transportista_record(record_id)
    assert registro.get("estatus") == ESTATUS_DESCARTADO, f"El camión quedó en '{registro.get('estatus')}'"

    patio = patio_obj.get_bitac_transportista_records(date_from=hoy, date_to=hoy, estatus=ESTATUS_COLUMNAS_KANBAN)
    assert record_id not in {r.get("_id") for r in patio}, "El camión descartado sigue en las columnas del patio"


@pytest.mark.integration
def test_asignar_y_quitar_anden(patio_obj, camion_en_arribo):
    """
    TB-091: el lápiz del Kanban asigna un andén y, para quitarlo, el front y
    la app mandan anden "" (bitacoras_transportistas/page.tsx:149). Tras
    quitarlo el camión debe quedar sin andén; si no, el andén se ve ocupado.
    """
    record_id = camion_en_arribo
    anden = patio_obj.get_andenes()[0]

    patio_obj.save_bitac_transportista_record(record_id, {"anden": anden})
    asignado = patio_obj.get_bitac_transportista_record(record_id).get("anden_asignado")
    assert asignado == anden, f"No se asignó el andén: {asignado!r}"

    patio_obj.save_bitac_transportista_record(record_id, {"anden": ""})
    despues = patio_obj.get_bitac_transportista_record(record_id).get("anden_asignado")
    assert not despues, f"El camión sigue con el andén {despues!r} después de quitarlo"


@pytest.mark.integration
def test_editar_embarque_no_pisa_la_empresa_transportista(patio_obj, camion_en_arribo):
    """
    TB-092: al editar la sección Embarque del detalle, la procedencia debe
    guardarse en su campo y la empresa transportista quedar igual. Si la
    procedencia se escribe sobre la empresa, el camión cambia de transportista.
    """
    record_id = camion_en_arribo

    patio_obj.save_bitac_transportista_record(record_id, {"embarque": EMBARQUE_EDITADO})

    registro = patio_obj.get_bitac_transportista_record(record_id)
    assert registro.get("proveedor_cliente") == EMBARQUE_EDITADO["proveedor_cliente"]
    assert registro.get("orden_de_compra") == EMBARQUE_EDITADO["no_orden_compra"]
    assert registro.get("procedencia") == EMBARQUE_EDITADO["procedencia"], (
        f"La procedencia no se guardó en su campo: {registro.get('procedencia')!r}"
    )
    assert registro.get("empresa_transportista") == LLEGADA_SIN_PASE["vehiculo"]["transportista"], (
        f"Se pisó la empresa transportista: {registro.get('empresa_transportista')!r}"
    )
