# coding: utf-8

"""
Vigencia, horario de la cita y ubicación del pase al dar acceso (do_access)
sin tocar preprod: se simulan el pase, sus entradas y la caseta, y se revisa
si se registra o no la entrada.
Notion: TB-178 a TB-180.
"""

import pytest

from .helpers import fecha_relativa
from ..data.nuevo_acceso_data import (
    LOCATION,
    AREA,
    QR_PASE_UNIT,
    PASE_DETALLE_ACTIVO,
    SIN_INGRESOS,
    VENCIDO_HACE_MIN,
    DENTRO_DE_TOLERANCIA_MIN,
    ENTRADA_REGISTRADA,
    CITA_FUERA_DE_TOLERANCIA_MIN,
    VIGENTE_POR_MIN,
    CONFIG_SIN_TOLERANCIA,
)


@pytest.mark.unit
def test_pase_con_mas_de_una_hora_de_vencido_no_da_acceso(accesos_no_api, mocker):
    """
    TB-178: un pase activo cuya fecha de caducidad pasó hace más de 1 hora
    (el margen de tolerancia) debe detenerse con el aviso de que ya pasó su
    vigencia y no registrar la entrada.
    """
    pase = {**PASE_DETALLE_ACTIVO, "fecha_de_caducidad": fecha_relativa(accesos_no_api, -VENCIDO_HACE_MIN)}
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="ya paso su fecha de vigencia"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


@pytest.mark.unit
def test_dentro_de_la_hora_de_tolerancia_el_pase_si_da_acceso(accesos_no_api, mocker):
    """
    TB-179: un pase activo que venció hace menos de 1 hora sigue dentro del
    margen de tolerancia: debe registrar la entrada en la ubicación y la
    caseta. Si lo rechaza, el visitante que llega un poco tarde no puede
    entrar aunque el margen se lo permite.
    """
    pase = {**PASE_DETALLE_ACTIVO, "fecha_de_caducidad": fecha_relativa(accesos_no_api, -DENTRO_DE_TOLERANCIA_MIN)}
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    mocker.patch.object(accesos_no_api, "validate_access_pass_location", return_value=False)
    registrar = mocker.patch.object(accesos_no_api, "_do_access", return_value=dict(ENTRADA_REGISTRADA))

    respuesta = accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})

    registrar.assert_called_once_with(pase, LOCATION, AREA, {})
    assert respuesta == ENTRADA_REGISTRADA


@pytest.mark.unit
def test_con_fecha_fija_no_se_puede_entrar_antes_de_la_tolerancia(accesos_no_api, mocker):
    """
    TB-180: un pase de fecha fija cuya cita es dentro de 1 hora, sin
    tolerancia configurada (15 min por defecto), debe detenerse con el aviso
    de que aún no es hora de entrada y no registrar la entrada.
    """
    pase = {
        **PASE_DETALLE_ACTIVO,
        "tipo_visita_pase": "fecha_fija",
        "fecha_de_expedicion": fecha_relativa(accesos_no_api, CITA_FUERA_DE_TOLERANCIA_MIN),
        "fecha_de_caducidad": fecha_relativa(accesos_no_api, VIGENTE_POR_MIN),
    }
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    mocker.patch.object(accesos_no_api, "get_config_accesos", return_value=dict(CONFIG_SIN_TOLERANCIA))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="no es hora de entrada"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()
