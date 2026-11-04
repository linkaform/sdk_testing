# coding: utf-8

"""
Notas de Caseta: crear una nota y consultarla en Pendientes, Cerradas y Todos
(notes.py: new_notes, get_notes, update_note).
Notion: TB-132 a TB-134.
"""

from datetime import datetime

import pytest
import pytz

from .fixtures import *
from ..data.notas_data import (
    LOCATION,
    AREA,
    NOTA_NUEVA,
    TODAS_LAS_AREAS,
    ESTATUS_ABIERTO,
    ESTATUS_CERRADO,
    ZONA_FECHA_CIERRE,
    NOTA_EDITADA,
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


@pytest.mark.integration
def test_cerrar_nota_la_pasa_a_cerradas(acceso_obj, nota_abierta):
    """
    TB-133: al cerrar una nota desde el modal Cerrar nota, debe quedar
    'cerrado' con fecha de cierre y quién la cerró, aparecer en Cerradas y
    salir de Pendientes. Si sigue en Pendientes, el guardia la vuelve a
    atender aunque ya se resolvió.
    """
    # Mismo payload que close-note-modal (notes.ts cerrarNota).
    fecha_cierre = datetime.now(pytz.timezone(ZONA_FECHA_CIERRE)).strftime("%Y-%m-%d %H:%M:%S")
    res = acceso_obj.update_notes(
        {"note_close_date": fecha_cierre, "note_status": ESTATUS_CERRADO}, nota_abierta["folio"]
    )
    assert res.get("status_code") in (200, 201, 202), f"No se pudo cerrar la nota: {res}"

    cerradas = acceso_obj.get_list_notes(LOCATION, TODAS_LAS_AREAS, status=ESTATUS_CERRADO, limit=LIMITE_LISTA)
    notas = {n["_id"]: n for n in cerradas["records"]}
    assert nota_abierta["_id"] in notas, "La nota cerrada no aparece en Cerradas"
    nota = notas[nota_abierta["_id"]]
    assert nota.get("note_status") == ESTATUS_CERRADO, f"La nota quedó '{nota.get('note_status')}'"
    assert nota.get("note_close_date"), "La nota cerrada no tiene fecha de cierre"
    assert nota.get("note_guard_close"), "La nota cerrada no dice quién la cerró"

    pendientes = acceso_obj.get_list_notes(LOCATION, TODAS_LAS_AREAS, status=ESTATUS_ABIERTO, limit=LIMITE_LISTA)
    assert nota_abierta["_id"] not in {n["_id"] for n in pendientes["records"]}, "La nota cerrada sigue en Pendientes"


@pytest.mark.integration
def test_editar_nota_guarda_texto_comentario_y_foto(acceso_obj, nota_abierta):
    """
    TB-134: al editar una nota desde el modal Editar nota, debe quedar con el
    título nuevo, el comentario agregado como texto y la foto. Si el
    comentario se guarda como lista, el front no lo puede mostrar.
    """
    res = acceso_obj.update_notes(NOTA_EDITADA, nota_abierta["folio"])
    assert res.get("status_code") in (200, 201, 202), f"No se pudo editar la nota: {res}"

    pendientes = acceso_obj.get_list_notes(LOCATION, TODAS_LAS_AREAS, status=ESTATUS_ABIERTO, limit=LIMITE_LISTA)
    notas = {n["_id"]: n for n in pendientes["records"]}
    assert nota_abierta["_id"] in notas, "La nota editada no aparece en Pendientes"
    nota = notas[nota_abierta["_id"]]

    assert nota.get("note") == NOTA_EDITADA["note"], f"El título no se editó: {nota.get('note')!r}"

    comentario = NOTA_EDITADA["note_comments"][0]
    textos = [c.get("note_comments") for c in nota.get("note_comments") or []]
    assert comentario in textos, f"El comentario no quedó como texto en la nota: {textos}"

    urls = [f.get("file_url") for f in nota.get("note_pic") or []]
    assert NOTA_EDITADA["note_pic"][0]["file_url"] in urls, f"La foto no se guardó: {nota.get('note_pic')}"
