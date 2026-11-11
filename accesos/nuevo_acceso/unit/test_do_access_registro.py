# coding: utf-8

"""
Registro de la entrada al dar acceso (do_access) sin tocar preprod: se
simulan el pase, sus entradas y la caseta, y se revisa si se registra la
entrada y en qué ubicación.
Notion: TB-183 y TB-184.
"""

import pytest

from .helpers import fecha_relativa
from ..data.nuevo_acceso_data import (
    LOCATION,
    AREA,
    QR_PASE_UNIT,
    PASE_DETALLE_ACTIVO,
    SIN_INGRESOS,
    VIGENTE_POR_MIN,
    ENTRADA_REGISTRADA,
    OTRA_UBICACION,
)


@pytest.mark.unit
def test_visitante_que_ya_esta_dentro_no_vuelve_a_entrar(accesos_no_api, mocker):
    """
    TB-183: con un pase válido cuyo visitante ya está dentro de la ubicación,
    do_access debe detenerse con el aviso de que ya se encuentra dentro y no
    registrar otra entrada. Si la registra, la bitácora muestra a la misma
    persona dentro dos veces.
    """
    pase = {**PASE_DETALLE_ACTIVO, "fecha_de_caducidad": fecha_relativa(accesos_no_api, VIGENTE_POR_MIN)}
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    mocker.patch.object(accesos_no_api, "validate_access_pass_location", return_value=True)
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="ya se encuentra dentro de una ubicacion"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


@pytest.mark.unit
def test_caseta_multiubicacion_registra_en_la_ubicacion_del_pase(accesos_no_api, mocker):
    """
    TB-184: en una caseta que atiende dos ubicaciones, un pase que solo es
    para la segunda debe dar acceso y registrar la entrada en la ubicación del
    pase, no en la de la caseta. Si se registra en la de la caseta, la persona
    aparece dentro de una planta a la que no tiene acceso.
    """
    pase = {
        **PASE_DETALLE_ACTIVO,
        "ubicacion": [OTRA_UBICACION],
        "fecha_de_caducidad": fecha_relativa(accesos_no_api, VIGENTE_POR_MIN),
    }
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION, OTRA_UBICACION])
    mocker.patch.object(accesos_no_api, "validate_access_pass_location", return_value=False)
    registrar = mocker.patch.object(accesos_no_api, "_do_access", return_value=dict(ENTRADA_REGISTRADA))

    respuesta = accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})

    registrar.assert_called_once_with(pase, OTRA_UBICACION, AREA, {})
    assert respuesta == ENTRADA_REGISTRADA
