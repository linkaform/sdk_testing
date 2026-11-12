# coding: utf-8

"""
Iniciar turno en la caseta (do_checkin) y sus validaciones, sin tocar
preprod: se simulan la caseta, el empleado y el guardado.
Notion: TB-269 a TB-273.
"""

import pytest

from ..data.turnos_data import (
    PUNTO_ESPERADO,
    GEO_LAT_LONG,
    GEO_LATITUDE_LONGITUDE,
    GEO_LISTA,
    GEO_FALSOS,
    USUARIO_GUARDIA,
    EMPLEADO_GUARDIA,
)


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

    mocker.patch.object(acc, "get_employee_data", return_value={})
    with pytest.raises(Exception, match="no tiene un empleado activo"):
        acc.require_active_employee(user_id, USUARIO_GUARDIA["name"])

    mocker.patch.object(acc, "get_employee_data", return_value=dict(EMPLEADO_GUARDIA))
    assert acc.require_active_employee(user_id, USUARIO_GUARDIA["name"]) == EMPLEADO_GUARDIA
