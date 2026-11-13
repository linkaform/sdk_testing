"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
from lkf_back import de
from ..data.fallas_data import (
    LOCATION,
    AREA,
    FALLA_UNIT,
    SEGUIMIENTO_UNIT,
    METADATA_FALLAS,
    GUARDADO_OK,
    FOLIO_FALLA,
    FOLIOS_FALLA,
    REGISTROS_FALLA,
    URL_REGISTRO,
    BORRADO_OK,
    OTRA_UBICACION,
    ESTATUS_ABIERTO,
    ESTATUS_TODOS,
    ESTATUS_RESUELTO,
    CERRAR_FALLA,
    EMPLEADO_FALLA,
    EDICION_OK,
)

C10_TRIGGERS = [
    "create_failure",
    "delete_failure",
    "fallas_base_match",
    "update_failure",
]


# --- create failure ---
@pytest.mark.unit
def test_crear_falla_guarda_la_ubicacion_y_la_caseta_juntas(accesos_no_api, mocker):
    """
    TB-217: con ubicación y caseta, create_failure debe guardar las dos en
    el catálogo de ubicaciones. Si se pierde una, la falla no aparece al
    filtrar por esa ubicación o caseta.
    """
    acc = accesos_no_api
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value=dict(METADATA_FALLAS))
    guardar = mocker.patch.object(acc.lkf_api, "post_forms_answers", return_value=dict(GUARDADO_OK))

    acc.create_failure(dict(FALLA_UNIT))

    answers = guardar.call_args.args[0]["answers"]
    assert answers[acc.fallas_fields["falla_ubicacion_catalog"]] == {
        acc.fallas_fields["falla_ubicacion"]: LOCATION,
        acc.fallas_fields["falla_caseta"]: AREA,
    }, f"El catálogo de ubicaciones quedó {answers[acc.fallas_fields['falla_ubicacion_catalog']]}"


@pytest.mark.unit
def test_crear_falla_guarda_la_falla_quien_reporta_y_el_responsable(accesos_no_api, mocker):
    """
    TB-218: create_failure debe guardar la falla con su objeto afectado en el
    catálogo de fallas, y quién reporta y el responsable de solucionarla en
    sus catálogos de empleados. Si falta uno, nadie sabe qué falló o a quién
    le toca resolverlo.
    """
    acc = accesos_no_api
    campos = acc.fallas_fields
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value=dict(METADATA_FALLAS))
    guardar = mocker.patch.object(acc.lkf_api, "post_forms_answers", return_value=dict(GUARDADO_OK))

    acc.create_failure(dict(FALLA_UNIT))

    answers = guardar.call_args.args[0]["answers"]
    assert answers[campos["falla_catalog"]] == {
        campos["falla"]: FALLA_UNIT["falla"],
        campos["falla_subconcepto"]: FALLA_UNIT["falla_objeto_afectado"],
    }, f"El catálogo de fallas quedó {answers[campos['falla_catalog']]}"
    assert answers[campos["falla_reporta_catalog"]] == {
        campos["falla_reporta_nombre"]: FALLA_UNIT["falla_reporta_nombre"],
    }, f"Quién reporta quedó {answers[campos['falla_reporta_catalog']]}"
    assert answers[campos["falla_responsable_solucionar_catalog"]] == {
        campos["falla_responsable_solucionar_nombre"]: FALLA_UNIT["falla_responsable_solucionar_nombre"],
    }, f"El responsable quedó {answers[campos['falla_responsable_solucionar_catalog']]}"


@pytest.mark.unit
def test_crear_falla_con_seguimiento_lo_guarda_con_lo_que_manda_el_front(accesos_no_api, mocker):
    """
    TB-219: add-falla.tsx manda los seguimientos con las llaves
    accion_correctiva_incidencia, fecha_inicio_seg y tiempo_transcurrido.
    create_failure debe guardarlos en el grupo de seguimiento con la acción,
    la fecha y el tiempo transcurrido. Si quedan vacíos, se pierde lo que ya
    se hizo para resolver la falla.
    """
    acc = accesos_no_api
    campos = acc.fallas_fields
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value=dict(METADATA_FALLAS))
    guardar = mocker.patch.object(acc.lkf_api, "post_forms_answers", return_value=dict(GUARDADO_OK))

    acc.create_failure({**FALLA_UNIT, "falla_grupo_seguimiento": [dict(SEGUIMIENTO_UNIT)]})

    seguimientos = guardar.call_args.args[0]["answers"][campos["falla_grupo_seguimiento"]]
    assert len(seguimientos) == 1, f"Se guardaron {len(seguimientos)} seguimientos, se mandó 1"
    seguimiento = seguimientos[0]
    assert seguimiento[campos["falla_accion_realizada"]] == SEGUIMIENTO_UNIT["accion_correctiva_incidencia"]
    assert seguimiento[campos["falla_fecha_seguimiento"]] == SEGUIMIENTO_UNIT["fecha_inicio_seg"]
    assert seguimiento[campos["falla_tiempo_transcurrido"]] == SEGUIMIENTO_UNIT["tiempo_transcurrido"]


# --- delete failure ---
@pytest.mark.unit
def test_folio_que_no_existe_da_error_y_no_borra(accesos_no_api, mocker):
    """
    TB-214: si el folio no se encuentra, delete_failure debe detenerse con
    el error de folio no encontrado y no mandar a borrar nada. Si borra, el
    guardia no se entera de que la falla que quería quitar no existía.
    """
    mocker.patch.object(accesos_no_api, "get_record_by_folio", return_value={})
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")

    with pytest.raises(Exception, match="No se encontro el folio correspondiente"):
        accesos_no_api.delete_failure([FOLIO_FALLA])
    borrar.assert_not_called()


@pytest.mark.unit
def test_sin_folios_da_error_y_no_borra(accesos_no_api, mocker):
    """
    TB-215: con la lista de folios vacía, delete_failure debe detenerse con
    el error de lista vacía y no mandar a borrar nada.
    """
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")

    with pytest.raises(Exception, match="Lista de folios vacia"):
        accesos_no_api.delete_failure([])
    borrar.assert_not_called()


@pytest.mark.unit
def test_varias_fallas_manda_a_borrar_cada_registro(accesos_no_api, mocker):
    """
    TB-216: con dos folios, delete_failure debe mandar a borrar en una sola
    llamada el registro de cada uno, y ninguno más. Si falta uno, la falla
    sigue en la lista; si sobra, se borra una que el guardia no eligió.
    """
    mocker.patch.object(
        accesos_no_api, "get_record_by_folio", side_effect=lambda folio, *a, **k: {"_id": REGISTROS_FALLA[folio]}
    )
    borrar = mocker.patch.object(accesos_no_api.lkf_api, "patch_record_list")
    mocker.patch.object(accesos_no_api, "check_status_code", return_value=dict(BORRADO_OK))

    res = accesos_no_api.delete_failure(list(FOLIOS_FALLA))

    assert res == BORRADO_OK
    borrar.assert_called_once()
    esperados = [URL_REGISTRO.format(REGISTROS_FALLA[folio]) for folio in FOLIOS_FALLA]
    assert borrar.call_args.args[0] == {"deleted_objects": esperados}, f"Mandó a borrar {borrar.call_args.args[0]}"


# --- fallas base match ---
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


# --- update failure ---
@pytest.mark.unit
def test_editar_falla_sin_cerrarla_la_deja_abierta_y_sin_fecha_de_solucion(accesos_no_api, mocker):
    """
    TB-220: al editar una falla con el payload de editar-falla (estatus
    'abierto'), update_failure debe guardar el estatus 'abierto' en el folio
    de la falla y no ponerle fecha de solución. Si le pone fecha, la falla
    parece resuelta aunque siga abierta.
    """
    acc = accesos_no_api
    mocker.patch.object(de(acc, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_FALLA))
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value={**EDICION_OK, "json": {}})

    res = acc.update_failure({**FALLA_UNIT, "falla_estatus": ESTATUS_ABIERTO}, FOLIO_FALLA)

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["folios"] == [FOLIO_FALLA]
    assert guardar.call_args.kwargs["form_id"] == acc.BITACORA_FALLAS
    answers = guardar.call_args.kwargs["answers"]
    assert answers[acc.fallas_fields["falla_estatus"]] == ESTATUS_ABIERTO, (
        f"El estatus quedó {answers[acc.fallas_fields['falla_estatus']]!r}"
    )
    assert res["json"]["falla_fecha_hora_solucion"] == "", (
        f"La falla abierta quedó con fecha de solución {res['json']['falla_fecha_hora_solucion']!r}"
    )
