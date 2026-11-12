# coding: utf-8

"""
Filtro de la lista de artículos perdidos (perdidos_base_match): ubicaciones
del header, caseta y estatus de la pestaña. Solo arma el filtro de Mongo,
así que se prueba directo, sin red.
Notion: TB-224 y TB-225.
"""

import pytest

from ..data.perdidos_data import LOCATION, AREA, OTRA_UBICACION, ESTATUS_PENDIENTE, ESTATUS_TODOS


@pytest.mark.unit
def test_filtro_toma_la_ubicacion_en_texto_o_en_lista(accesos_no_api):
    """
    TB-224: una ubicación en texto debe filtrar exacto por ella; la lista de
    ubicaciones del header debe filtrar con $in y ganar sobre la de texto.
    Sin ninguna no debe filtrar por ubicación. Si no, la lista trae
    artículos de otras plantas o ninguno.
    """
    acc = accesos_no_api
    ubicacion = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_SALIDA_OBJ_ID}.{acc.mf['ubicacion']}"

    filtro = acc.perdidos_base_match(location=LOCATION)
    assert filtro["form_id"] == acc.BITACORA_OBJETOS_PERDIDOS
    assert filtro["deleted_at"] == {"$exists": False}
    assert filtro[ubicacion] == LOCATION

    varias = acc.perdidos_base_match(location=LOCATION, locations=[LOCATION, OTRA_UBICACION])
    assert varias[ubicacion] == {"$in": [LOCATION, OTRA_UBICACION]}, f"Filtró {varias[ubicacion]!r}"

    sin_ubicacion = acc.perdidos_base_match()
    assert ubicacion not in sin_ubicacion, f"Sin ubicación filtró {sin_ubicacion[ubicacion]!r}"


@pytest.mark.unit
def test_filtro_usa_el_estatus_de_la_pestana_y_la_caseta(accesos_no_api):
    """
    TB-225: Pendientes manda el estatus 'pendiente' y la caseta; los dos
    deben entrar al filtro. Todos no manda estatus y no debe filtrar por
    estatus. Si no, Pendientes mezcla artículos ya entregados o Todos deja
    fuera algunos.
    """
    acc = accesos_no_api
    estatus = f"answers.{acc.perdidos_fields['estatus_perdido']}"
    caseta = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_SALIDA_OBJ_ID}.{acc.mf['nombre_area_salida']}"

    pendientes = acc.perdidos_base_match(location=LOCATION, area=AREA, status=ESTATUS_PENDIENTE)
    assert pendientes[estatus] == ESTATUS_PENDIENTE
    assert pendientes[caseta] == AREA

    todos = acc.perdidos_base_match(location=LOCATION, status=ESTATUS_TODOS)
    assert estatus not in todos, f"Todos filtró por estatus {todos[estatus]!r}"
