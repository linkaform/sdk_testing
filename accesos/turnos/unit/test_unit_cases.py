"""Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS.

./lkf test corre SOLO este archivo cuando cambia alguna funcion de
C10_TRIGGERS. Aqui van los casos principales de cada funcion y las
validaciones mas importantes; los demas unitarios de la seccion viven en
otros archivos de unit/ y se corren a mano.
"""

import pytest
from lkf_back import de
from ..data.turnos_data import (
    PUNTO_ESPERADO,
    GEO_LAT_LONG,
    GEO_LATITUDE_LONGITUDE,
    GEO_LISTA,
    GEO_FALSOS,
    USUARIO_GUARDIA,
    EMPLEADO_GUARDIA,
    LOCATION,
    AREA,
    ROL_GUARDIA,
    ROL_ADMIN,
    CHECKIN_ABIERTO,
    GUARDADO_OK,
    GUARDIA_ID,
    ZONA_TURNO,
    ESTATUS_ENTRADA,
    ASISTENCIA_OK,
)

C10_TRIGGERS = [
    "do_checkin",
    "do_checkout",
    "parse_geolocation",
    "require_active_employee",
]


def checkin_simulado(acceso_obj, mocker, caseta_abierta):
    """
    Simula lo que do_checkin consulta antes de guardar: la caseta, el usuario y
    su empleado. Regresa los mocks de crear el turno y de sumarse al abierto.
    """
    mocker.patch.object(acceso_obj, "is_boot_available", return_value=caseta_abierta)
    mocker.patch.object(acceso_obj, "get_open_checkin", return_value={})
    mocker.patch.object(acceso_obj.lkf_api, "get_user_by_id", return_value=dict(USUARIO_GUARDIA))
    mocker.patch.object(de(acceso_obj, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_GUARDIA))
    crear = mocker.patch.object(acceso_obj.lkf_api, "post_forms_answers")
    sumar = mocker.patch.object(acceso_obj, "update_guards_checkin")
    return crear, sumar


# --- checkin validaciones ---
@pytest.mark.unit
def test_geolocalizacion_se_normaliza_y_descarta_puntos_falsos(accesos_no_api):
    """
    TB-269: la web y la app mandan la ubicación como {lat, long},
    {latitude, longitude} o [lat, long]; parse_geolocation debe regresar
    siempre [lat, long]. Con 0,0, fuera de rango o texto debe regresar None
    para no guardar un punto falso en el turno.
    """
    acc = accesos_no_api

    for formato in (GEO_LAT_LONG, GEO_LATITUDE_LONGITUDE, GEO_LISTA):
        assert acc.parse_geolocation(formato) == PUNTO_ESPERADO, f"{formato} quedó {acc.parse_geolocation(formato)}"
    for falso in GEO_FALSOS:
        assert acc.parse_geolocation(falso) is None, f"{falso!r} quedó {acc.parse_geolocation(falso)}"


@pytest.mark.unit
def test_sin_empleado_activo_no_se_puede_iniciar_turno(accesos_no_api, mocker):
    """
    TB-270: require_active_employee debe detenerse con el error de que el
    usuario no tiene un empleado activo; con empleado activo lo regresa. Si
    deja pasar, alguien dado de baja abre la caseta.
    """
    acc = accesos_no_api
    user_id = acc.user["user_id"]

    mocker.patch.object(de(acc, "get_employee_data"), "get_employee_data", return_value={})
    with pytest.raises(Exception, match="no tiene un empleado activo"):
        acc.require_active_employee(user_id, USUARIO_GUARDIA["name"])

    mocker.patch.object(de(acc, "get_employee_data"), "get_employee_data", return_value=dict(EMPLEADO_GUARDIA))
    assert acc.require_active_employee(user_id, USUARIO_GUARDIA["name"]) == EMPLEADO_GUARDIA


@pytest.mark.unit
def test_guardia_sin_la_caseta_configurada_no_puede_iniciar_turno(accesos_no_api, mocker):
    """
    TB-271: con la caseta cerrada, un guardia que no tiene esa caseta en su
    configuración debe detenerse con el error de que no puede hacer check-in
    ahí, y no crear el turno. Si lo crea, abre una caseta que no le toca.
    """
    acc = accesos_no_api
    crear, sumar = checkin_simulado(acc, mocker, caseta_abierta=False)
    mocker.patch.object(acc, "get_users_by_location_area", return_value=[])

    with pytest.raises(Exception, match="no puede hacer check-in en la caseta"):
        acc.do_checkin(LOCATION, AREA, employee_list=[])
    crear.assert_not_called()
    sumar.assert_not_called()


@pytest.mark.unit
def test_guardia_con_turno_abierto_en_otra_caseta_no_puede_entrar(accesos_no_api, mocker):
    """
    TB-272: un guardia que ya tiene turno abierto ('in') en otra caseta debe
    detenerse con el error de que está registrado en otra caseta, y no crear
    el turno. Si entra, queda en dos casetas a la vez.
    """
    acc = accesos_no_api
    user_id = acc.user["user_id"]
    crear, sumar = checkin_simulado(acc, mocker, caseta_abierta=False)
    mocker.patch.object(acc, "get_users_by_location_area", return_value=[{"user_id": user_id}])
    mocker.patch.object(acc, "get_employee_checkin_status", return_value={user_id: {"status": "in"}})

    with pytest.raises(Exception, match="registrados en otra caseta"):
        acc.do_checkin(LOCATION, AREA, employee_list=[])
    crear.assert_not_called()
    sumar.assert_not_called()


@pytest.mark.unit
def test_con_la_caseta_abierta_el_guardia_se_suma_al_turno(accesos_no_api, mocker):
    """
    TB-273: con la caseta ya abierta, do_checkin debe sumar al guardia al
    turno abierto y no crear otro. De los roles que manda el front, los de
    administración que el usuario no tiene asignados se descartan y los
    normales pasan tal cual. Si crea otro turno, la caseta queda con dos
    abiertos; si deja pasar el rol de admin, el guardia ve menús que no le
    tocan.
    """
    acc = accesos_no_api
    crear, sumar = checkin_simulado(acc, mocker, caseta_abierta=True)
    sumar.return_value = dict(GUARDADO_OK)
    mocker.patch.object(acc, "last_check_in", dict(CHECKIN_ABIERTO), create=True)
    mocker.patch.object(acc, "get_roles_usuario", return_value=[ROL_GUARDIA])
    mocker.patch.object(acc, "assign_unassigned_rondines_on_checkin")

    res = acc.do_checkin(LOCATION, AREA, employee_list=[], roles=[ROL_GUARDIA, ROL_ADMIN])

    assert res == GUARDADO_OK
    crear.assert_not_called()
    sumar.assert_called_once()
    assert sumar.call_args.args[1] == CHECKIN_ABIERTO["_id"], "Se sumó a otro turno"
    assert sumar.call_args.args[7] == [ROL_GUARDIA], f"Roles que se mandaron: {sumar.call_args.args[7]}"


# --- checkout ---
def turno_guardado(acceso_obj):
    """Registro del turno abierto en la caseta con un guardia que sigue dentro."""
    f = acceso_obj.checkin_fields
    empleados = de(acceso_obj, "CONF_AREA_EMPLEADOS_CAT_OBJ_ID").CONF_AREA_EMPLEADOS_CAT_OBJ_ID
    apoyo = de(acceso_obj, "CONF_AREA_EMPLEADOS_AP_CAT_OBJ_ID").CONF_AREA_EMPLEADOS_AP_CAT_OBJ_ID
    return {
        "_id": CHECKIN_ABIERTO["_id"],
        "folio": "1-TURNO",
        "timezone": ZONA_TURNO,
        "answers": {
            empleados: {acceso_obj.f["location"]: LOCATION, acceso_obj.f["area"]: AREA},
            f["guard_group"]: [{
                apoyo: {acceso_obj.mf["id_usuario"]: [GUARDIA_ID]},
                f["checkin_status"]: ESTATUS_ENTRADA,
            }],
        },
    }


def checkout_simulado(acceso_obj, mocker, caseta_abierta=True):
    """
    Simula lo que do_checkout consulta antes de guardar: el usuario, la caseta
    y el turno. Regresa los mocks del guardado y de cerrar la asistencia.
    """
    mocker.patch.object(acceso_obj.lkf_api, "get_user_by_id", return_value=dict(USUARIO_GUARDIA))
    mocker.patch.object(acceso_obj, "is_boot_available", return_value=caseta_abierta)
    mocker.patch.object(acceso_obj, "get_record_by_id", return_value=turno_guardado(acceso_obj))
    mocker.patch.object(acceso_obj.lkf_api, "get_metadata", return_value={})
    guardar = mocker.patch.object(acceso_obj.lkf_api, "patch_record", return_value=dict(GUARDADO_OK))
    asistencia = mocker.patch.object(acceso_obj, "close_guards_attendance", return_value=ASISTENCIA_OK)
    return guardar, asistencia


@pytest.mark.unit
def test_cerrar_turno_sin_el_id_del_turno_da_error(accesos_no_api, mocker):
    """
    TB-274: sin checkin_id, do_checkout debe detenerse con el error de que no
    encontró un turno válido y no guardar nada. Si sigue, cierra un turno que
    no se sabe cuál es.
    """
    acc = accesos_no_api
    guardar, _ = checkout_simulado(acc, mocker)

    with pytest.raises(Exception, match="No encontramos un checking valido"):
        acc.do_checkout(checkin_id=None, location=LOCATION, area=AREA)
    guardar.assert_not_called()


@pytest.mark.unit
def test_cerrar_turno_con_la_caseta_cerrada_da_error(accesos_no_api, mocker):
    """
    TB-275: si la caseta ya está cerrada, do_checkout debe detenerse con el
    error de que no se puede cerrar sin haberla abierto y no guardar nada. Si
    guarda, el turno queda cerrado dos veces con fechas distintas.
    """
    acc = accesos_no_api
    guardar, _ = checkout_simulado(acc, mocker, caseta_abierta=False)

    with pytest.raises(Exception, match="sin antes haber hecho check-in"):
        acc.do_checkout(checkin_id=CHECKIN_ABIERTO["_id"], location=LOCATION, area=AREA)
    guardar.assert_not_called()
