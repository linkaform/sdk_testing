"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
from lkf_back import de
from ..data.notas_data import (
    LOCATION,
    AREA,
    NOTA_NUEVA,
    EMPLEADO_NOTA,
    FECHA_SERVIDOR,
    COMENTARIOS_NOTA,
    TODAS_LAS_AREAS,
    ESTATUS_TODOS,
    FACET_NOTA,
    NOTAS_EN_TOTAL,
    NOTAS_POR_PAGINA,
    SALTAR_NOTAS,
    ESTATUS_ABIERTO,
    ESTATUS_TURNO,
    OTRA_UBICACION,
    DIA_FILTRO,
    FOLIO_NOTA,
    CERRAR_NOTA,
    ESTATUS_CERRADO,
    NOTA_EDITADA,
)

C10_TRIGGERS = [
    "create_note",
    "get_list_notes",
    "notas_base_match",
    "update_notes",
]


# --- create note ---
@pytest.mark.unit
def test_create_note_guarda_nota_abierta_con_ubicacion_caseta_guardia_y_fecha(accesos_no_api, mocker):
    """
    TB-161: con el payload de + Nueva Nota, create_note debe guardar el
    título, el estatus 'abierto', la ubicación y la caseta, el guardia que la
    crea y la fecha de apertura en la zona del empleado. Si falta alguno, la
    nota no sale en la caseta correcta o no se sabe quién la dejó.
    """
    mocker.patch.object(accesos_no_api.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(de(accesos_no_api, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_NOTA))
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
    guardia = answers[de(accesos_no_api, "CONF_AREA_EMPLEADOS_CAT_OBJ_ID").CONF_AREA_EMPLEADOS_CAT_OBJ_ID]
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
    mocker.patch.object(de(accesos_no_api, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_NOTA))
    mocker.patch.object(accesos_no_api, "today_str", return_value=FECHA_SERVIDOR)
    guardar = mocker.patch.object(accesos_no_api.lkf_api, "post_forms_answers", return_value={"status_code": 201})

    accesos_no_api.create_note(LOCATION, AREA, {**NOTA_NUEVA, "note_comments": list(COMENTARIOS_NOTA)})

    nf = accesos_no_api.notes_fields
    renglones = guardar.call_args.args[0]["answers"][nf["note_comments_group"]]
    assert [r[nf["note_comments"]] for r in renglones] == COMENTARIOS_NOTA, f"Los comentarios quedaron {renglones}"


# --- get list notes ---
@pytest.mark.unit
def test_lista_de_notas_aplica_el_buscador_y_pagina(accesos_no_api, mocker):
    """
    TB-172: con un filtro del buscador, 10 por página y saltando 10, la
    consulta debe llevar la condición del buscador, saltar 10 y traer 10, y
    la respuesta debe decir página 2 de 3 con 25 notas. Si no, el buscador no
    filtra o la paginación repite o salta notas.
    """
    nota = {"_id": "6650a1b2c3d4e5f6a7b8c9d0", "note": NOTA_NUEVA["note"]}
    consulta = mocker.patch.object(
        accesos_no_api.cr, "aggregate", side_effect=[[dict(nota)], [{"total": NOTAS_EN_TOTAL}]]
    )
    facets = [{"key": FACET_NOTA, "values": [NOTA_NUEVA["note"]], "exact": False}]

    lista = accesos_no_api.get_list_notes(
        LOCATION, TODAS_LAS_AREAS, status=ESTATUS_TODOS, limit=NOTAS_POR_PAGINA, offset=SALTAR_NOTAS, facets=facets
    )

    pasos = consulta.call_args_list[0].args[0]
    match = pasos[0]["$match"]
    assert match.get("$and"), f"La consulta no lleva la condición del buscador: {match}"
    assert {"$skip": SALTAR_NOTAS} in pasos, f"La consulta no salta {SALTAR_NOTAS}: {pasos}"
    assert {"$limit": NOTAS_POR_PAGINA} in pasos, f"La consulta no trae {NOTAS_POR_PAGINA}: {pasos}"
    assert lista["total_records"] == NOTAS_EN_TOTAL
    assert lista["actual_page"] == 2, f"Página {lista['actual_page']}"
    assert lista["total_pages"] == 3, f"Total de páginas {lista['total_pages']}"
    assert len(lista["records"]) == 1


# --- notas base match ---
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


@pytest.mark.unit
def test_las_ubicaciones_del_header_filtran_con_todas_a_la_vez(accesos_no_api):
    """
    TB-170: el buscador manda las ubicaciones elegidas en el header
    (locations). Con dos ubicaciones, el filtro debe traer las notas de las
    dos ($in), aunque también venga location. Si solo usa location, la lista
    esconde las notas de la otra ubicación.
    """
    acc = accesos_no_api
    ubicacion = f"answers.{acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID}.{acc.f['location']}"

    filtro = acc.notas_base_match(LOCATION, TODAS_LAS_AREAS, ESTATUS_TODOS, locations=[LOCATION, OTRA_UBICACION])
    assert filtro[ubicacion] == {"$in": [LOCATION, OTRA_UBICACION]}, f"El filtro de ubicación quedó {filtro[ubicacion]!r}"


@pytest.mark.unit
def test_filtrar_un_solo_dia_trae_el_dia_completo(accesos_no_api):
    """
    TB-171: con la misma fecha en desde y hasta, el filtro de fecha de
    apertura debe cubrir el día completo, de 00:00:00 a 23:59:59. Si compara
    solo la fecha, las notas de ese día con hora no salen.
    """
    acc = accesos_no_api
    apertura = f"answers.{acc.notes_fields['note_open_date']}"

    filtro = acc.notas_base_match(LOCATION, TODAS_LAS_AREAS, ESTATUS_TODOS, dateFrom=DIA_FILTRO, dateTo=DIA_FILTRO)
    assert filtro[apertura] == {"$gte": f"{DIA_FILTRO} 00:00:00", "$lte": f"{DIA_FILTRO} 23:59:59"}, (
        f"El filtro de fecha quedó {filtro[apertura]!r}"
    )


# --- update notes ---
@pytest.mark.unit
def test_cerrar_nota_guarda_estatus_y_fecha_de_cierre(accesos_no_api, mocker):
    """
    TB-163: con el payload de close-note-modal, update_notes debe guardar la
    nota como 'cerrado' con la fecha de cierre en la zona del empleado, sobre
    el folio de esa nota. Si no, la nota sigue en Pendientes o sin fecha.
    """
    mocker.patch.object(de(accesos_no_api, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_NOTA))
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
def test_editar_nota_no_la_cierra(accesos_no_api, mocker):
    """
    TB-166: editar una nota (sin note_status 'cerrado') no debe ponerle fecha
    de cierre ni quién la cerró, ni consultar al empleado. Si lo hace, una
    nota abierta aparece como cerrada por alguien que solo la editó.
    """
    empleado = mocker.patch.object(de(accesos_no_api, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_NOTA))
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
