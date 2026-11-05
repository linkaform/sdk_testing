# coding: utf-8

"""
Notas abiertas en la página de Turnos de la caseta (get_shift_data → notes).
Notion: TB-137.
"""

from datetime import datetime

import pytest
import pytz

from .fixtures import *
from ..data.notas_data import (
    LOCATION,
    AREA,
    ESTATUS_CERRADO,
    ZONA_FECHA_CIERRE,
)


@pytest.mark.integration
def test_notas_abiertas_salen_en_el_turno_de_la_caseta(acceso_obj, nota_abierta):
    """
    TB-137: la página de Turnos muestra las notas abiertas de la caseta. Una
    nota recién creada en esa caseta debe salir ahí y, ya cerrada, dejar de
    salir. Si no sale, el guardia que entra no ve lo pendiente; si sigue
    después de cerrarla, la vuelve a atender.
    """
    turno = acceso_obj.get_shift_data(booth_location=LOCATION, booth_area=AREA)
    notas_turno = {n["_id"] for n in turno["notes"]["records"]}
    assert nota_abierta["_id"] in notas_turno, "La nota abierta no sale en el turno de la caseta"

    # Mismo payload que close-note-modal (notes.ts cerrarNota).
    fecha_cierre = datetime.now(pytz.timezone(ZONA_FECHA_CIERRE)).strftime("%Y-%m-%d %H:%M:%S")
    res = acceso_obj.update_notes(
        {"note_close_date": fecha_cierre, "note_status": ESTATUS_CERRADO}, nota_abierta["folio"]
    )
    assert res.get("status_code") in (200, 201, 202), f"No se pudo cerrar la nota: {res}"

    turno = acceso_obj.get_shift_data(booth_location=LOCATION, booth_area=AREA)
    notas_turno = {n["_id"] for n in turno["notes"]["records"]}
    assert nota_abierta["_id"] not in notas_turno, "La nota cerrada sigue en el turno de la caseta"
