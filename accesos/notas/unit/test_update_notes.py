# coding: utf-8

"""
Cerrar y editar una nota (update_notes) sin tocar preprod: se simulan el
empleado, la fecha y el guardado, y se revisa lo que update_notes manda a
guardar.
Notion: TB-163 y TB-164.
"""

import pytest

from ..data.notas_data import (
    EMPLEADO_NOTA,
    FECHA_SERVIDOR,
    FOLIO_NOTA,
    CERRAR_NOTA,
    ESTATUS_CERRADO,
)


@pytest.mark.unit
def test_cerrar_nota_guarda_estatus_y_fecha_de_cierre(accesos_no_api, mocker):
    """
    TB-163: con el payload de close-note-modal, update_notes debe guardar la
    nota como 'cerrado' con la fecha de cierre en la zona del empleado, sobre
    el folio de esa nota. Si no, la nota sigue en Pendientes o sin fecha.
    """
    mocker.patch.object(accesos_no_api, "get_employee_data", return_value=dict(EMPLEADO_NOTA))
    fecha = mocker.patch.object(accesos_no_api, "today_str", return_value=FECHA_SERVIDOR)
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    accesos_no_api.update_notes(dict(CERRAR_NOTA), FOLIO_NOTA)

    nf = accesos_no_api.notes_fields
    kwargs = guardar.call_args.kwargs
    assert kwargs["form_id"] == accesos_no_api.ACCESOS_NOTAS
    assert kwargs["folios"] == [FOLIO_NOTA]
    assert kwargs["answers"][nf["note_status"]] == ESTATUS_CERRADO
    fecha.assert_called_once_with(EMPLEADO_NOTA["timezone"], date_format="datetime")
    assert kwargs["answers"][nf["note_close_date"]] == FECHA_SERVIDOR, (
        f"La fecha de cierre quedó {kwargs['answers'][nf['note_close_date']]!r}"
    )


@pytest.mark.unit
def test_cerrar_nota_guarda_quien_la_cerro_donde_la_lista_lo_lee(accesos_no_api, mocker):
    """
    TB-164: al cerrar, el nombre del empleado que la cierra debe quedar en el
    catálogo del que get_list_notes lee note_guard_close. Si se guarda en otro
    lado, la lista de Cerradas no dice quién cerró la nota (ticket 2610-1515).
    """
    mocker.patch.object(accesos_no_api, "get_employee_data", return_value=dict(EMPLEADO_NOTA))
    mocker.patch.object(accesos_no_api, "today_str", return_value=FECHA_SERVIDOR)
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    accesos_no_api.update_notes(dict(CERRAR_NOTA), FOLIO_NOTA)

    nf = accesos_no_api.notes_fields
    answers = guardar.call_args.kwargs["answers"]
    cerro = answers.get(nf["note_catalog_guard_close"], {}).get(nf["note_guard_close"])
    assert cerro == EMPLEADO_NOTA["worker_name"], (
        f"Quién cerró quedó {cerro!r} en el catálogo que lee la lista; se guardó en {sorted(answers)}"
    )
