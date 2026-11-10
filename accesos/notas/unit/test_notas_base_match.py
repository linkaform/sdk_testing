# coding: utf-8

"""
Filtro de la lista de notas (notas_base_match): Pendientes, Cerradas, Todos,
el turno, las ubicaciones del header y las fechas. Es una función que solo
arma el filtro de Mongo, así que se prueba directo, sin red.
Notion: TB-168 y TB-169.
"""

import pytest

from ..data.notas_data import (
    LOCATION,
    AREA,
    TODAS_LAS_AREAS,
    ESTATUS_ABIERTO,
    ESTATUS_TODOS,
    ESTATUS_TURNO,
)


@pytest.mark.unit
def test_pendientes_filtra_por_estatus_ubicacion_y_caseta(accesos_no_api):
    """
    TB-168: Pendientes de una caseta debe filtrar la forma de notas, sin las
    borradas, por estatus 'abierto', la ubicación y la caseta. Con el área
    'todas' no debe filtrar por caseta. Si falta un filtro, la lista mezcla
    notas de otras casetas o ya cerradas.
    """
    acc = accesos_no_api
    ubicacion = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{acc.f['location']}"
    caseta = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{acc.f['area']}"
    estatus = f"answers.{acc.notes_fields['note_status']}"

    filtro = acc.notas_base_match(LOCATION, AREA, ESTATUS_ABIERTO)
    assert filtro["form_id"] == acc.ACCESOS_NOTAS
    assert filtro["deleted_at"] == {"$exists": False}
    assert filtro[estatus] == ESTATUS_ABIERTO
    assert filtro[ubicacion] == LOCATION
    assert filtro[caseta] == AREA

    todas = acc.notas_base_match(LOCATION, TODAS_LAS_AREAS, ESTATUS_ABIERTO)
    assert caseta not in todas, f"Con área 'todas' filtró por caseta: {todas[caseta]!r}"


@pytest.mark.unit
def test_todos_y_el_turno_no_filtran_por_estatus(accesos_no_api):
    """
    TB-169: la pestaña Todos manda estatus '' y la página de Turnos manda
    'dia'; ninguno de los dos debe filtrar por estatus. Si filtran, Todos no
    trae las cerradas o el turno no muestra las notas del día.
    """
    acc = accesos_no_api
    estatus = f"answers.{acc.notes_fields['note_status']}"

    for valor in (ESTATUS_TODOS, ESTATUS_TURNO):
        filtro = acc.notas_base_match(LOCATION, TODAS_LAS_AREAS, valor)
        assert estatus not in filtro, f"Con estatus {valor!r} filtró por {filtro[estatus]!r}"
