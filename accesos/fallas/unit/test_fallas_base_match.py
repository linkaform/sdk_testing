# coding: utf-8

"""
Filtro de la lista de fallas (fallas_base_match): ubicaciones del header,
estatus de la pestaña y folio. Solo arma el filtro de Mongo, así que se
prueba directo, sin red.
Notion: TB-212 y TB-213.
"""

import pytest

from ..data.fallas_data import LOCATION, OTRA_UBICACION, ESTATUS_ABIERTO, ESTATUS_TODOS, FOLIO_FALLA


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


@pytest.mark.unit
def test_filtro_usa_el_estatus_y_el_folio_cuando_vienen(accesos_no_api):
    """
    TB-213: Abiertas manda el estatus 'abierto' y el detalle manda el folio;
    los dos deben entrar al filtro. Todos no manda estatus y no debe filtrar
    por estatus ni por folio. Si no, Abiertas mezcla fallas cerradas o Todos
    deja fuera algunas.
    """
    acc = accesos_no_api
    estatus = f"answers.{acc.fallas_fields['falla_estatus']}"

    abiertas = acc.fallas_base_match(LOCATION, status=ESTATUS_ABIERTO, folio=FOLIO_FALLA)
    assert abiertas[estatus] == ESTATUS_ABIERTO
    assert abiertas["folio"] == FOLIO_FALLA

    todos = acc.fallas_base_match(LOCATION, status=ESTATUS_TODOS)
    assert estatus not in todos, f"Todos filtró por estatus {todos[estatus]!r}"
    assert "folio" not in todos, f"Todos filtró por folio {todos['folio']!r}"
