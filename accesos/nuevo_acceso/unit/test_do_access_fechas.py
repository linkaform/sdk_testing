# coding: utf-8

"""
Vigencia, horario de la cita y ubicación del pase al dar acceso (do_access)
sin tocar preprod: se simulan el pase, sus entradas y la caseta, y se revisa
si se registra o no la entrada.
Notion: TB-178 a TB-182.
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
    OTRA_UBICACION,
)


@pytest.mark.unit
def test_con_fecha_fija_no_se_puede_entrar_despues_de_la_tolerancia(accesos_no_api, mocker):
    """
    TB-181: un pase de fecha fija cuya cita fue hace 1 hora, sin tolerancia
    configurada (15 min por defecto), debe detenerse con el aviso de que el
    tiempo de tolerancia expiró y no registrar la entrada.
    """
    pase = {
        **PASE_DETALLE_ACTIVO,
        "tipo_visita_pase": "fecha_fija",
        "fecha_de_expedicion": fecha_relativa(accesos_no_api, -CITA_FUERA_DE_TOLERANCIA_MIN),
        "fecha_de_caducidad": fecha_relativa(accesos_no_api, VIGENTE_POR_MIN),
    }
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value=pase)
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    mocker.patch.object(accesos_no_api, "get_booth_locations", return_value=[LOCATION])
    mocker.patch.object(accesos_no_api, "get_config_accesos", return_value=dict(CONFIG_SIN_TOLERANCIA))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="El tiempo de tolerancia ha expirado"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()
