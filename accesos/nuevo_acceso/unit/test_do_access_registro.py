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
