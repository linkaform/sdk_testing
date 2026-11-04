# coding: utf-8

"""
Notas de Caseta: crear una nota y consultarla en Pendientes, Cerradas y Todos
(notes.py: new_notes, get_notes, update_note).
Notion: TB-132.
"""

import pytest

from .fixtures import *
from ..data.notas_data import (
    LOCATION,
    AREA,
    NOTA_NUEVA,
    TODAS_LAS_AREAS,
    ESTATUS_ABIERTO,
    LIMITE_LISTA,
)


@pytest.mark.integration
def test_crear_nota_la_muestra_en_pendientes(acceso_obj):
    """
    TB-132: una nota creada desde + Nueva Nota debe aparecer en Pendientes
    (status 'abierto') con su texto, también al filtrar por su caseta. Si no
    aparece, el siguiente guardia no se entera de lo que quedó pendiente en
    el turno.
    """
    res = acceso_obj.create_note(LOCATION, AREA, NOTA_NUEVA)
    nota_id = (res.get("json") or {}).get("id")
    assert res.get("status_code") in (200, 201, 202) and nota_id, f"No se pudo crear la nota: {res}"

    pendientes = acceso_obj.get_list_notes(LOCATION, TODAS_LAS_AREAS, status=ESTATUS_ABIERTO, limit=LIMITE_LISTA)
    notas = {n["_id"]: n for n in pendientes["records"]}

    assert nota_id in notas, "La nota nueva no aparece en Pendientes"
    nota = notas[nota_id]
    assert nota.get("note_status") == ESTATUS_ABIERTO, f"La nota quedó '{nota.get('note_status')}'"
    assert nota.get("note") == NOTA_NUEVA["note"]

    # La caseta se guarda en el área de la ubicación: es lo que filtra la lista.
    de_la_caseta = acceso_obj.get_list_notes(LOCATION, AREA, status=ESTATUS_ABIERTO, limit=LIMITE_LISTA)
    assert nota_id in {n["_id"] for n in de_la_caseta["records"]}, f"La nota no aparece al filtrar por la caseta {AREA}"
