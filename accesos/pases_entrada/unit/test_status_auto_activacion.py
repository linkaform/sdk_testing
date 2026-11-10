# coding: utf-8

"""
Auto activación del pase ("Activar pase por defecto" de + Nuevo Pase,
_status_auto_activacion): cuándo regresa None para seguir el flujo normal y
cuándo deja el pase activo, en proceso o vencido. Función directa, sin
preprod.
Notion: TB-192 a TB-195.
"""

import pytest

from .helpers import answers_pase, fecha_hasta
from ..data.pases_entrada_data import (
    NOMBRE_PASE_UNIT,
    DIAS_VIGENTE,
    AUTO_ACTIVACION_NO,
    REQUIERE_FOTO_E_IDENTIFICACION,
)


@pytest.mark.unit
def test_sin_auto_activacion_sigue_el_flujo_normal(accesos_no_api):
    """
    TB-192: con auto_activacion "no", o sin la llave, debe regresar None
    para que create_access_pass siga su flujo normal. Si regresa un estatus,
    el pase se activa aunque el anfitrión no lo pidió.
    """
    campos = {"walkin_nombre": NOMBRE_PASE_UNIT, "fecha_desde_hasta": fecha_hasta(accesos_no_api, DIAS_VIGENTE)}

    con_no = answers_pase(accesos_no_api, auto_activacion=AUTO_ACTIVACION_NO, **campos)
    assert accesos_no_api._status_auto_activacion(con_no, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION) is None

    sin_llave = answers_pase(accesos_no_api, **campos)
    assert accesos_no_api._status_auto_activacion(sin_llave, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION) is None
