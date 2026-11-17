# coding: utf-8

"""
Guardias de apoyo en el turno abierto: agregarlo (update_guards_checkin:
add-guard-modal) y darle salida (do_checkout con guards: tabla de guardias de
apoyo) sin tocar preprod. Se simulan el turno y el guardado.
Notion: TB-125 y TB-126.
"""

from lkf_back import de

from ..data.guardias_apoyo_data import (
    LOCATION,
    AREA,
    TURNO_ID,
    ZONA_TURNO,
    GUARDIA_APOYO,
    GUARDIA_APOYO_ID,
    ESTATUS_ENTRADA,
    GUARDADO_OK,
    GUARDIA_PRINCIPAL_ID,
    ESTATUS_SALIDA,
    ASISTENCIA_OK,
)


def test_agregar_guardia_de_apoyo_lo_suma_al_turno_sin_crear_otro(accesos_no_api, mocker):
    """
    TB-125: con el payload de add-guard-modal, update_guards_checkin debe
    agregar al guardia como renglón nuevo del grupo de guardias del turno
    abierto, con su id, su nombre, puesto guardia de apoyo y estatus entrada,
    sin crear otro registro de turno. Si crea otro turno, la caseta queda con
    dos turnos abiertos.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "get_record_timezone", return_value=ZONA_TURNO)
    mocker.patch.object(acc, "get_employee_checkin_status", return_value={})
    mocker.patch.object(acc, "do_attendance")
    crear = mocker.patch.object(acc.lkf_api, "post_forms_answers")
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value=dict(GUARDADO_OK))

    acc.update_guards_checkin([dict(GUARDIA_APOYO)], TURNO_ID, LOCATION, AREA)

    crear.assert_not_called()
    guardar.assert_called_once()
    assert guardar.call_args.kwargs["record_id"] == [TURNO_ID]
    renglones = guardar.call_args.kwargs["answers"][acc.mf["guard_group"]]
    assert list(renglones) == ["-1"], f"El guardia no se agregó como renglón nuevo: {list(renglones)}"
    guardia = renglones["-1"]
    apoyo = de(acc, "CONF_AREA_EMPLEADOS_AP_CAT_OBJ_ID").CONF_AREA_EMPLEADOS_AP_CAT_OBJ_ID
    assert guardia[apoyo][acc.mf["id_usuario"]] == [GUARDIA_APOYO_ID]
    assert guardia[apoyo][acc.f["worker_name_b"]] == GUARDIA_APOYO["name"]
    assert guardia[acc.checkin_fields["checkin_position"]] == acc.support_guard
    assert guardia[acc.checkin_fields["checkin_status"]] == ESTATUS_ENTRADA


def turno_con_apoyo(acceso_obj):
    """Registro del turno abierto con el guardia principal y uno de apoyo, los dos dentro."""
    f = acceso_obj.checkin_fields
    empleados = de(acceso_obj, "CONF_AREA_EMPLEADOS_CAT_OBJ_ID").CONF_AREA_EMPLEADOS_CAT_OBJ_ID
    apoyo = de(acceso_obj, "CONF_AREA_EMPLEADOS_AP_CAT_OBJ_ID").CONF_AREA_EMPLEADOS_AP_CAT_OBJ_ID
    return {
        "_id": TURNO_ID,
        "folio": "1-TURNO",
        "timezone": ZONA_TURNO,
        "answers": {
            empleados: {acceso_obj.f["location"]: LOCATION, acceso_obj.f["area"]: AREA},
            f["guard_group"]: [
                {apoyo: {acceso_obj.mf["id_usuario"]: [GUARDIA_PRINCIPAL_ID]}, f["checkin_status"]: ESTATUS_ENTRADA},
                {apoyo: {acceso_obj.mf["id_usuario"]: [GUARDIA_APOYO_ID]}, f["checkin_status"]: ESTATUS_ENTRADA},
            ],
        },
    }


def test_dar_salida_a_un_guardia_de_apoyo_deja_el_turno_abierto(accesos_no_api, mocker):
    """
    TB-126: con el payload de la tabla de guardias de apoyo (guards con su id,
    guard_id y checkin_id), do_checkout debe marcar la salida solo de ese
    guardia, cerrarle su asistencia y dejar el turno abierto con el guardia
    principal dentro. Si cierra la caseta, el guardia principal se queda sin
    turno.
    """
    acc = accesos_no_api
    f = acc.checkin_fields
    mocker.patch.object(acc.lkf_api, "get_user_by_id", return_value={"name": GUARDIA_APOYO["name"]})
    mocker.patch.object(acc, "is_boot_available", return_value=True)
    mocker.patch.object(acc, "get_record_by_id", return_value=turno_con_apoyo(acc))
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value={})
    guardar = mocker.patch.object(acc.lkf_api, "patch_record", return_value=dict(GUARDADO_OK))
    asistencia = mocker.patch.object(acc, "close_guards_attendance", return_value=ASISTENCIA_OK)

    acc.do_checkout(checkin_id=TURNO_ID, location=LOCATION, area=AREA, guards=[GUARDIA_APOYO_ID], guard_id=GUARDIA_APOYO_ID)

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["record_id"] == TURNO_ID
    answers = guardar.call_args.kwargs["data"]["answers"]
    principal, apoyo = answers[f["guard_group"]]
    assert apoyo[f["checkin_status"]] == ESTATUS_SALIDA, f"El guardia de apoyo quedó {apoyo[f['checkin_status']]!r}"
    assert principal[f["checkin_status"]] == ESTATUS_ENTRADA, "El guardia principal también salió del turno"
    assert answers.get(f["checkin_type"]) != "cerrada", "La caseta se cerró al dar salida al guardia de apoyo"
    assert asistencia.call_args.args[0] == [GUARDIA_APOYO_ID], f"Se cerró la asistencia de {asistencia.call_args.args[0]}"
