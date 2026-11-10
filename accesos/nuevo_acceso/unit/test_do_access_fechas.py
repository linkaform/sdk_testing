# coding: utf-8

"""
Vigencia, horario de la cita y ubicación del pase al dar acceso (do_access)
sin tocar preprod: se simulan el pase, sus entradas y la caseta, y se revisa
si se registra o no la entrada.
Notion: TB-178.
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
