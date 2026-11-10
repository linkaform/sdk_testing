# coding: utf-8

"""
Validaciones del pase al dar acceso (do_access) sin tocar preprod: se simulan
el pase y su conteo de entradas, y se revisa que no se registre la entrada
cuando el pase no debe pasar.
Notion: TB-173 a TB-176.
"""

import json
from datetime import datetime

import pytest
import pytz

from ..data.nuevo_acceso_data import (
    LOCATION,
    AREA,
    QR_PASE_UNIT,
    PASE_DETALLE_ACTIVO,
    SIN_INGRESOS,
    DIAS_SEMANA,
    ZONA_DIA_ACCESO,
)


@pytest.mark.unit
def test_pase_cancelado_no_da_acceso(accesos_no_api, mocker):
    """
    TB-173: un pase cancelado debe detenerse con el error de pase cancelado
    y no registrar la entrada. Si se registra, entra alguien cuyo pase ya
    se dio de baja.
    """
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value={**PASE_DETALLE_ACTIVO, "estatus": "cancelado"})
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="El pase esta cancelado"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


@pytest.mark.unit
def test_pase_vencido_no_da_acceso(accesos_no_api, mocker):
    """
    TB-174: un pase vencido debe detenerse con el error de pase vencido y no
    registrar la entrada. Si se registra, entra alguien fuera de la vigencia
    que le dieron.
    """
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value={**PASE_DETALLE_ACTIVO, "estatus": "vencido"})
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="El pase esta vencido"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


@pytest.mark.unit
def test_pase_en_proceso_no_da_acceso(accesos_no_api, mocker):
    """
    TB-175: un pase en proceso (el visitante no ha subido lo que le piden)
    debe detenerse con el aviso de que no se ha completado y no registrar la
    entrada. Si se registra, entra alguien sin foto o identificación.
    """
    mocker.patch.object(accesos_no_api, "get_detail_access_pass", return_value={**PASE_DETALLE_ACTIVO, "estatus": "proceso"})
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="El pase no se ha sido completado"):
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()


@pytest.mark.unit
def test_pase_limitado_a_ciertos_dias_no_deja_entrar_otro_dia(accesos_no_api, mocker):
    """
    TB-176: un pase activo que solo vale ciertos días no debe dejar entrar
    hoy si hoy no es uno de ellos, y el aviso debe decir qué días sí puede
    entrar. Si deja entrar, el pase no respeta los días que le dieron.
    """
    hoy = DIAS_SEMANA[datetime.now(pytz.timezone(ZONA_DIA_ACCESO)).weekday()]
    permitidos = [dia for dia in DIAS_SEMANA if dia != hoy][:2]
    mocker.patch.object(
        accesos_no_api, "get_detail_access_pass", return_value={**PASE_DETALLE_ACTIVO, "limitado_a_dias": permitidos}
    )
    mocker.patch.object(accesos_no_api, "get_count_ingresos", return_value=dict(SIN_INGRESOS))
    registrar = mocker.patch.object(accesos_no_api, "_do_access")

    with pytest.raises(Exception, match="Este pase no te permite ingresar hoy") as error:
        accesos_no_api.do_access(QR_PASE_UNIT, LOCATION, AREA, {})
    registrar.assert_not_called()
    aviso = json.loads(str(error.value))["exception"]["msg"][0]
    for dia in permitidos:
        assert dia.capitalize() in aviso, f"El aviso no dice que puede entrar el {dia}: {aviso}"
