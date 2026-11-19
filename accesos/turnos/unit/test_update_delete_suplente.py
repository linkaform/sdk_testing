# coding: utf-8

"""
Quitar el suplente del turno (update_delete_suplente) sin tocar preprod: se
simulan el turno abierto del usuario y el guardado, y se revisa qué se manda
a guardar en el folio del turno.
Notion: TB-278.
"""

import pytest

from ..data.turnos_data import (
    FOLIO_TURNO,
    SUPLENTE_VACIO,
    GUARDADO_OK,
)


@pytest.mark.bug(1577)
def test_quitar_el_suplente_lo_borra_del_turno(accesos_no_api, mocker):
    """
    TB-278: con el nombre del suplente vacío, update_delete_suplente debe
    mandar el campo del suplente vacío al folio del turno para borrarlo. Si
    manda los answers vacíos, el suplente se queda en el turno aunque el
    guardia lo haya quitado. Ticket 2610-1577: con el nombre vacío manda
    answers vacíos.
    """
    acc = accesos_no_api
    usuario = acc.user.get("user_id")
    mocker.patch.object(acc, "get_employee_checkin_status", return_value={usuario: {"folio": FOLIO_TURNO}})
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value=dict(GUARDADO_OK))

    acc.update_delete_suplente(SUPLENTE_VACIO)

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["folios"] == [FOLIO_TURNO]
    answers = guardar.call_args.kwargs["answers"]
    campo = acc.checkin_fields["nombre_suplente"]
    assert campo in answers, f"No se mandó el campo del suplente para borrarlo; answers: {answers!r}"
    assert answers[campo] == SUPLENTE_VACIO
