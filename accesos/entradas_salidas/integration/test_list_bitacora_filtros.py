# coding: utf-8

"""
Lista de la bitácora (list_bitacora2 → get_list_bitacora): filtros de las
opciones del menú Entradas, Salidas y Accesos de hoy.
Notion: TB-044 a TB-047.
"""

import pytest
from datetime import datetime
from pytz import timezone

from .fixtures import *
from ..data.bitacora_data import LOCATION, AREA, LIMITE_LISTA


@pytest.mark.integration
def test_list_bitacora_filtro_entradas_solo_regresa_entradas(acceso_obj, pase_dentro):
    """
    TB-044: la opción "Entradas" filtra la lista por status 'entrada'. Debe
    regresar solo visitas abiertas de la ubicación consultada e incluir la
    entrada recién registrada; si no, el guardia no ve quién sigue dentro.
    """
    _, entrada = pase_dentro

    res = acceso_obj.get_list_bitacora(
        location=LOCATION,
        area=AREA,
        dynamic_filters=[{"key": "status", "value": ["entrada"]}],
        limit=LIMITE_LISTA,
    )
    registros = res["records"]

    assert registros, "La lista de Entradas viene vacía"
    assert all(r["status_visita"] == "Entrada" for r in registros), (
        f"La lista de Entradas trae otros estatus: {sorted({r['status_visita'] for r in registros})}"
    )
    assert all(r["ubicacion"] == LOCATION for r in registros), (
        f"La lista trae otras ubicaciones: {sorted({r['ubicacion'] for r in registros})}"
    )
    assert entrada["_id"] in {r["_id"] for r in registros}, "La entrada recién registrada no aparece en la lista"


@pytest.mark.integration
def test_list_bitacora_filtro_salidas_solo_regresa_salidas(acceso_obj, pase_dentro):
    """
    TB-045: la opción "Salidas" filtra la lista por status 'salida'. Debe
    regresar solo visitas cerradas de la ubicación consultada e incluir la
    salida recién registrada; si no, el historial de salidas queda incompleto.
    """
    folio, entrada = pase_dentro
    acceso_obj.do_out(folio, LOCATION, AREA)

    res = acceso_obj.get_list_bitacora(
        location=LOCATION,
        area=AREA,
        dynamic_filters=[{"key": "status", "value": ["salida"]}],
        limit=LIMITE_LISTA,
    )
    registros = res["records"]

    assert registros, "La lista de Salidas viene vacía"
    assert all(r["status_visita"] == "Salida" for r in registros), (
        f"La lista de Salidas trae otros estatus: {sorted({r['status_visita'] for r in registros})}"
    )
    assert all(r["ubicacion"] == LOCATION for r in registros), (
        f"La lista trae otras ubicaciones: {sorted({r['ubicacion'] for r in registros})}"
    )
    assert entrada["_id"] in {r["_id"] for r in registros}, "La salida recién registrada no aparece en la lista"


@pytest.mark.integration
def test_list_bitacora_accesos_de_hoy_solo_regresa_entradas_de_hoy(acceso_obj, pase_dentro):
    """
    TB-046: la opción "Accesos de hoy" filtra con filterDate='today' en la
    zona horaria del usuario. Debe regresar solo visitas cuya fecha de entrada
    es de hoy e incluir la entrada recién registrada.
    """
    _, entrada = pase_dentro
    hoy = datetime.now(timezone(acceso_obj.user["timezone"])).strftime("%Y-%m-%d")

    res = acceso_obj.get_list_bitacora(
        location=LOCATION,
        area=AREA,
        filterDate="today",
        limit=LIMITE_LISTA,
    )
    registros = res["records"]

    assert registros, "La lista de Accesos de hoy viene vacía"
    assert all((r.get("fecha_entrada") or "").startswith(hoy) for r in registros), (
        f"La lista de hoy ({hoy}) trae entradas de otros días: "
        f"{sorted({(r.get('fecha_entrada') or '')[:10] for r in registros})}"
    )
    assert entrada["_id"] in {r["_id"] for r in registros}, "La entrada recién registrada no aparece en Accesos de hoy"


@pytest.mark.integration
@pytest.mark.xfail(
    reason="Bug confirmado: bitacora_base_match aplica filterDate siempre sobre fecha_entrada; "
           "en Salidas + hoy no aparece quien entró ayer y salió hoy.",
    strict=True,
)
def test_list_bitacora_salidas_de_hoy_filtra_por_fecha_de_salida(acceso_obj):
    """
    TB-047: al combinar la opción "Salidas" con el filtro "hoy", la fecha debe
    aplicarse sobre la fecha de salida. Si se aplica sobre la de entrada, quien
    entró ayer y salió hoy no aparece en las salidas del día.
    """
    campo_entrada = f"answers.{acceso_obj.mf['fecha_entrada']}"
    campo_salida = f"answers.{acceso_obj.mf['fecha_salida']}"

    filtro = acceso_obj.bitacora_base_match(
        location=LOCATION,
        area=AREA,
        filterDate="today",
        dynamic_filters=[{"key": "status", "value": ["salida"]}],
    )

    assert campo_salida in filtro, f"El filtro de hoy no se aplica sobre fecha_salida: {filtro}"
    assert campo_entrada not in filtro, f"El filtro de hoy se aplica sobre fecha_entrada: {filtro}"
