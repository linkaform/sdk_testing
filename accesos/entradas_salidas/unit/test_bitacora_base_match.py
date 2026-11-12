# coding: utf-8

"""
Filtro de la lista de Entradas & Salidas (bitacora_base_match): ubicación,
caseta, filtros del panel y el campo de fecha según la pestaña. Solo arma el
filtro de Mongo, así que se prueba directo, sin red.
Notion: TB-264 a TB-266.
"""

import pytest

from ..data.bitacora_data import LOCATION, AREA, OTRA_LOCATION


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
