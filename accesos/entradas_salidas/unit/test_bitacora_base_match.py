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
    PERFIL_PANEL,
    VISITA_A_PANEL,
    FILTROS_PANEL,
    FILTRO_DESCONOCIDO,
)


@pytest.mark.unit
def test_filtros_del_panel_entran_al_filtro_y_los_desconocidos_se_ignoran(accesos_no_api):
    """
    TB-266: los filtros del panel (estatus, perfil, a quién visita y
    ubicación) deben entrar al filtro con $in en su campo, y una llave que el
    backend no conoce no debe cambiar el filtro. Si uno no entra, el guardia
    filtra y la lista no cambia.
    """
    acc = accesos_no_api
    mf = acc.mf

    filtro = acc.bitacora_base_match(dynamic_filters=FILTROS_PANEL)

    assert filtro[f"answers.{mf['tipo_registro']}"] == {"$in": ["entrada"]}
    assert filtro[f"answers.{acc.PASE_ENTRADA_OBJ_ID}.{mf['nombre_perfil']}"] == {"$in": [PERFIL_PANEL]}
    visita_a = f"answers.{mf['grupo_visitados']}.{acc.CONF_AREA_EMPLEADOS_CAT_OBJ_ID}.{mf['nombre_empleado']}"
    assert filtro[visita_a] == {"$in": [VISITA_A_PANEL]}
    ubicacion = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{mf['ubicacion']}"
    assert filtro[ubicacion] == {"$in": [LOCATION, OTRA_LOCATION]}

    assert acc.bitacora_base_match(dynamic_filters=FILTRO_DESCONOCIDO) == acc.bitacora_base_match(), (
        "Una llave desconocida cambió el filtro"
    )
