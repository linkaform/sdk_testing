# coding: utf-8

"""
Filtro de la lista de concesiones (concesionados_base_match): ubicaciones del
header y estado de la pestaña. Solo arma el filtro de Mongo, así que se
prueba directo, sin red.
Notion: TB-234.
"""

import pytest

from ..data.concesionados_data import LOCATION, OTRA_UBICACION, ESTADO_ABIERTO, ESTADO_TODOS


@pytest.mark.unit
def test_filtro_usa_la_ubicacion_y_el_estado_de_la_pestana(accesos_no_api):
    """
    TB-234: una ubicación en texto debe filtrar exacto por ella y la lista de
    ubicaciones del header con $in, ganando sobre la de texto. Pendientes
    manda el estado 'abierto' y debe entrar al filtro; Todos no filtra por
    estado. Si no, la lista mezcla concesiones de otras plantas o ya
    devueltas.
    """
    acc = accesos_no_api
    ubicacion = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{acc.mf['ubicacion']}"
    estado = f"answers.{acc.cons_f['status_concesion']}"

    filtro = acc.concesionados_base_match(location=LOCATION, status=ESTADO_ABIERTO)
    assert filtro["form_id"] == acc.CONCESSIONED_ARTICULOS
    assert filtro["deleted_at"] == {"$exists": False}
    assert filtro[ubicacion] == LOCATION
    assert filtro[estado] == ESTADO_ABIERTO

    varias = acc.concesionados_base_match(location=LOCATION, locations=[LOCATION, OTRA_UBICACION])
    assert varias[ubicacion] == {"$in": [LOCATION, OTRA_UBICACION]}, f"Filtró {varias[ubicacion]!r}"

    todos = acc.concesionados_base_match(location=LOCATION, status=ESTADO_TODOS)
    assert estado not in todos, f"Todos filtró por estado {todos[estado]!r}"
