# coding: utf-8

"""
Filtro de la lista de fallas (fallas_base_match): ubicaciones del header,
estatus de la pestaña y folio. Solo arma el filtro de Mongo, así que se
prueba directo, sin red.
Notion: TB-212 y TB-213.
"""

import pytest

from ..data.fallas_data import LOCATION, OTRA_UBICACION


@pytest.mark.unit
def test_filtro_toma_la_ubicacion_como_texto_o_lista(accesos_no_api):
    """
    TB-212: el front manda las ubicaciones del header en lista y otros
    callers una sola en texto; las dos formas deben filtrar con $in, sin las
    vacías. Sin ubicación no debe filtrar por ubicación. Si no, la lista
    trae fallas de otras plantas o ninguna.
    """
    acc = accesos_no_api
    ubicacion = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{acc.fallas_fields['falla_ubicacion']}"

    filtro = acc.fallas_base_match(LOCATION)
    assert filtro["form_id"] == acc.BITACORA_FALLAS
    assert filtro["deleted_at"] == {"$exists": False}
    assert filtro[ubicacion] == {"$in": [LOCATION]}

    varias = acc.fallas_base_match([LOCATION, "", OTRA_UBICACION])
    assert varias[ubicacion] == {"$in": [LOCATION, OTRA_UBICACION]}, f"Filtró {varias[ubicacion]!r}"

    sin_ubicacion = acc.fallas_base_match([])
    assert ubicacion not in sin_ubicacion, f"Sin ubicación filtró {sin_ubicacion[ubicacion]!r}"
