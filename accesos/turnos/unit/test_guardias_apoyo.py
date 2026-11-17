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
