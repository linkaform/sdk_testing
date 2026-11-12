# coding: utf-8

"""
Filtro de la lista de artículos perdidos (perdidos_base_match): ubicaciones
del header, caseta y estatus de la pestaña. Solo arma el filtro de Mongo,
así que se prueba directo, sin red.
Notion: TB-224 y TB-225.
"""

import pytest

from ..data.perdidos_data import LOCATION, OTRA_UBICACION


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
