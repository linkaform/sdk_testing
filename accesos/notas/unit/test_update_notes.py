# coding: utf-8

"""
Cerrar y editar una nota (update_notes) sin tocar preprod: se simulan el
empleado, la fecha y el guardado, y se revisa lo que update_notes manda a
guardar.
Notion: TB-163 a TB-167.
"""

import pytest

from ..data.notas_data import (
    EMPLEADO_NOTA,
    FECHA_SERVIDOR,
    FOLIO_NOTA,
    CERRAR_NOTA,
    ESTATUS_CERRADO,
    NOTA_EDITADA,
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


@pytest.mark.unit
def test_editar_nota_agrega_el_comentario_como_texto(accesos_no_api, mocker):
    """
    TB-165: edit-note-modal manda el comentario nuevo como lista de un texto.
    El renglón que se agrega al grupo de comentarios debe guardar el texto,
    no la lista; si guarda la lista, el comentario se ve como ['...'] o no se
    muestra (ticket 2610-1516).
    """
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    accesos_no_api.update_notes(dict(NOTA_EDITADA), FOLIO_NOTA)

    nf = accesos_no_api.notes_fields
    grupo = guardar.call_args.kwargs["answers"][nf["note_comments_group"]]
    renglon = list(grupo.values())[0]
    assert renglon[nf["note_comments"]] == NOTA_EDITADA["note_comments"][0], (
        f"El comentario nuevo quedó {renglon[nf['note_comments']]!r}"
    )


@pytest.mark.unit
def test_editar_nota_no_la_cierra(accesos_no_api, mocker):
    """
    TB-166: editar una nota (sin note_status 'cerrado') no debe ponerle fecha
    de cierre ni quién la cerró, ni consultar al empleado. Si lo hace, una
    nota abierta aparece como cerrada por alguien que solo la editó.
    """
    empleado = mocker.patch.object(accesos_no_api, "get_employee_data", return_value=dict(EMPLEADO_NOTA))
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    accesos_no_api.update_notes(dict(NOTA_EDITADA), FOLIO_NOTA)

    nf = accesos_no_api.notes_fields
    answers = guardar.call_args.kwargs["answers"]
    assert nf["note_close_date"] not in answers, f"Editar puso fecha de cierre: {answers[nf['note_close_date']]!r}"
    assert accesos_no_api.CONF_AREA_EMPLEADOS_AP_CAT_OBJ_ID not in answers, "Editar guardó quién cerró la nota"
    assert nf["note_status"] not in answers, f"Editar cambió el estatus a {answers[nf['note_status']]!r}"
    empleado.assert_not_called()


@pytest.mark.unit
def test_editar_nota_no_borra_lo_que_viene_vacio(accesos_no_api, mocker):
    """
    TB-167: edit-note-modal manda note_file vacío ([]) cuando no se agrega
    archivo. Ese campo no debe ir en lo que se guarda; si va, la edición
    borra el archivo que ya tenía la nota. La foto que sí viene se guarda.
    """
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "patch_multi_record", return_value={"status_code": 202})

    accesos_no_api.update_notes(dict(NOTA_EDITADA), FOLIO_NOTA)

    nf = accesos_no_api.notes_fields
    answers = guardar.call_args.kwargs["answers"]
    assert nf["note_file"] not in answers, f"Editar mandó el archivo vacío: {answers[nf['note_file']]!r}"
    assert answers[nf["note_pic"]] == NOTA_EDITADA["note_pic"]
