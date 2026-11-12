# coding: utf-8

"""
Filtro de la lista de Entradas & Salidas (bitacora_base_match): ubicación,
caseta, filtros del panel y el campo de fecha según la pestaña. Solo arma el
filtro de Mongo, así que se prueba directo, sin red.
Notion: TB-264 a TB-266.
"""

import pytest

from ..data.bitacora_data import (
    LOCATION,
    AREA,
    OTRA_LOCATION,
    FILTRO_ENTRADAS,
    FILTRO_SALIDAS,
    FILTRO_RANGO,
    DIA_CONSULTA,
    FIN_DIA_CONSULTA,
)


@pytest.mark.unit
def test_filtro_usa_la_ubicacion_en_texto_o_en_lista_y_la_caseta(accesos_no_api):
    """
    TB-264: una ubicación en texto debe filtrar exacto y una lista de
    ubicaciones con $in; la caseta entra al filtro. Siempre se filtra la
    forma de bitácora sin los registros borrados. Si no, la lista mezcla
    visitas de otras plantas o casetas.
    """
    acc = accesos_no_api
    ubicacion = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{acc.mf['ubicacion']}"
    caseta = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{acc.mf['nombre_area']}"

    filtro = acc.bitacora_base_match(LOCATION, AREA)
    assert filtro["form_id"] == acc.BITACORA_ACCESOS
    assert filtro["deleted_at"] == {"$exists": False}
    assert filtro[ubicacion] == LOCATION
    assert filtro[caseta] == AREA

    varias = acc.bitacora_base_match([LOCATION, OTRA_LOCATION])
    assert varias[ubicacion] == {"$in": [LOCATION, OTRA_LOCATION]}, f"Filtró {varias[ubicacion]!r}"


@pytest.mark.unit
def test_en_salidas_la_fecha_que_se_filtra_es_la_de_salida(accesos_no_api):
    """
    TB-265: en Salidas (estatus 'salida') el rango de fechas debe aplicarse a
    la fecha de salida; en Entradas, a la de entrada. Si Salidas filtra por
    la entrada, quien entró ayer y salió hoy no aparece en las salidas de hoy.
    """
    acc = accesos_no_api
    fecha_salida = f"answers.{acc.mf['fecha_salida']}"
    fecha_entrada = f"answers.{acc.mf['fecha_entrada']}"
    rango = {"$gte": DIA_CONSULTA, "$lte": FIN_DIA_CONSULTA}

    salidas = acc.bitacora_base_match(
        LOCATION, AREA, dateFrom=DIA_CONSULTA, dateTo=DIA_CONSULTA, filterDate=FILTRO_RANGO, dynamic_filters=FILTRO_SALIDAS
    )
    assert salidas.get(fecha_salida) == rango, f"Salidas filtró la fecha de salida con {salidas.get(fecha_salida)!r}"
    assert fecha_entrada not in salidas, "Salidas filtró por la fecha de entrada"

    entradas = acc.bitacora_base_match(
        LOCATION, AREA, dateFrom=DIA_CONSULTA, dateTo=DIA_CONSULTA, filterDate=FILTRO_RANGO, dynamic_filters=FILTRO_ENTRADAS
    )
    assert entradas.get(fecha_entrada) == rango, f"Entradas filtró la fecha de entrada con {entradas.get(fecha_entrada)!r}"
