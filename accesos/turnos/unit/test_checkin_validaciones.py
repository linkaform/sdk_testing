# coding: utf-8

"""
Iniciar turno en la caseta (do_checkin) y sus validaciones, sin tocar
preprod: se simulan la caseta, el empleado y el guardado.
Notion: TB-269 a TB-273.
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
)


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
