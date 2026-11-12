# coding: utf-8

"""
Filtro de la lista de paquetes (paqueteria_base_match): ubicaciones del
header, caseta y estatus de la pestaña. Solo arma el filtro de Mongo, así
que se prueba directo, sin red.
Notion: TB-245.
"""

import pytest

from ..data.paqueteria_data import LOCATION, AREA, OTRA_UBICACION, ESTATUS_GUARDADO, ESTATUS_TODOS


@pytest.mark.unit
def test_filtro_usa_la_ubicacion_la_caseta_y_el_estatus_de_la_pestana(accesos_no_api):
    """
    TB-245: una ubicación en texto debe filtrar exacto y la lista de
    ubicaciones del header con $in, ganando sobre la de texto. Pendientes
    manda el estatus 'guardado' y la caseta; los dos deben entrar al filtro.
    Todos no filtra por estatus. Si no, la lista mezcla paquetes de otras
    casetas o ya entregados.
    """
    acc = accesos_no_api
    campos = acc.paquetes_fields
    ubicacion = f"answers.{campos['ubicacion_paqueteria']}"
    caseta = f"answers.{campos['area_paqueteria']}"
    estatus = f"answers.{campos['estatus_paqueteria']}"

    filtro = acc.paqueteria_base_match(location=LOCATION, area=AREA, status=ESTATUS_GUARDADO)
    assert filtro["form_id"] == acc.PAQUETERIA
    assert filtro["deleted_at"] == {"$exists": False}
    assert filtro[ubicacion] == LOCATION
    assert filtro[caseta] == AREA
    assert filtro[estatus] == ESTATUS_GUARDADO

    varias = acc.paqueteria_base_match(location=LOCATION, locations=[LOCATION, OTRA_UBICACION])
    assert varias[ubicacion] == {"$in": [LOCATION, OTRA_UBICACION]}, f"Filtró {varias[ubicacion]!r}"

    todos = acc.paqueteria_base_match(location=LOCATION, status=ESTATUS_TODOS)
    assert estatus not in todos, f"Todos filtró por estatus {todos[estatus]!r}"
