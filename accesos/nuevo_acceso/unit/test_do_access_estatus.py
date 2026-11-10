# coding: utf-8

"""
Validaciones del pase al dar acceso (do_access) sin tocar preprod: se simulan
el pase y su conteo de entradas, y se revisa que no se registre la entrada
cuando el pase no debe pasar.
Notion: TB-173 a TB-175.
"""

import pytest

from ..data.nuevo_acceso_data import (
    LOCATION,
    AREA,
    QR_PASE_UNIT,
    PASE_DETALLE_ACTIVO,
    SIN_INGRESOS,
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
