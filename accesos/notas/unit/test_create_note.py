# coding: utf-8

"""
Crear una nota (create_note) sin tocar preprod: se simulan la metadata de la
forma, el empleado, la fecha y el guardado, y se revisa lo que create_note
manda a guardar.
Notion: TB-161 y TB-162.
"""

import pytest

from ..data.notas_data import (
    LOCATION,
    AREA,
    NOTA_NUEVA,
    EMPLEADO_NOTA,
    FECHA_SERVIDOR,
    COMENTARIOS_NOTA,
)


@pytest.mark.unit
def test_create_note_guarda_nota_abierta_con_ubicacion_caseta_guardia_y_fecha(accesos_no_api, mocker):
    """
    TB-161: con el payload de + Nueva Nota, create_note debe guardar el
    título, el estatus 'abierto', la ubicación y la caseta, el guardia que la
    crea y la fecha de apertura en la zona del empleado. Si falta alguno, la
    nota no sale en la caseta correcta o no se sabe quién la dejó.
    """
    mocker.patch.object(accesos_no_api.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(accesos_no_api, "get_employee_data", return_value=dict(EMPLEADO_NOTA))
    fecha = mocker.patch.object(accesos_no_api, "today_str", return_value=FECHA_SERVIDOR)
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "post_forms_answers", return_value={"status_code": 201})

    accesos_no_api.create_note(LOCATION, AREA, dict(NOTA_NUEVA))

    nf = accesos_no_api.notes_fields
    answers = guardar.call_args.args[0]["answers"]
    assert answers[nf["note"]] == NOTA_NUEVA["note"]
    assert answers[nf["note_status"]] == "abierto"
    area = answers[accesos_no_api.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID]
    assert area[accesos_no_api.f["location"]] == LOCATION
    assert area[accesos_no_api.f["area"]] == AREA
    guardia = answers[accesos_no_api.CONF_AREA_EMPLEADOS_CAT_OBJ_ID]
    assert guardia[accesos_no_api.f["worker_name"]] == EMPLEADO_NOTA["worker_name"]
    fecha.assert_called_once_with(EMPLEADO_NOTA["timezone"], date_format="datetime")
    assert answers[nf["note_open_date"]] == FECHA_SERVIDOR


@pytest.mark.unit
def test_create_note_guarda_cada_comentario_en_su_renglon(accesos_no_api, mocker):
    """
    TB-162: el front manda la descripción como lista. Con dos comentarios,
    el grupo de comentarios de la nota debe tener dos renglones, cada uno con
    su texto. Si se juntan o se pierde uno, el siguiente turno no lee todo.
    """
    mocker.patch.object(accesos_no_api.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(accesos_no_api, "get_employee_data", return_value=dict(EMPLEADO_NOTA))
    mocker.patch.object(accesos_no_api, "today_str", return_value=FECHA_SERVIDOR)
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "post_forms_answers", return_value={"status_code": 201})

    accesos_no_api.create_note(LOCATION, AREA, {**NOTA_NUEVA, "note_comments": list(COMENTARIOS_NOTA)})

    nf = accesos_no_api.notes_fields
    renglones = guardar.call_args.args[0]["answers"][nf["note_comments_group"]]
    assert [r[nf["note_comments"]] for r in renglones] == COMENTARIOS_NOTA, f"Los comentarios quedaron {renglones}"
