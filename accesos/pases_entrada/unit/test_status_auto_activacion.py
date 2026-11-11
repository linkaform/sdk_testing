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
    DIAS_VENCIDO,
    AUTO_ACTIVACION_SI,
    AUTO_ACTIVACION_NO,
    URL_PADRE,
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


@pytest.mark.unit
def test_auto_activacion_deja_activo_sin_foto_ni_identificacion(accesos_no_api):
    """
    TB-193: con auto_activacion "sí", nombre y fecha vigente, el pase debe
    quedar 'activo' aunque la ubicación pida foto e identificación y no las
    traiga. Si queda en proceso, el guardia espera a un visitante que el
    anfitrión ya quería dejar pasar.
    """
    answers = answers_pase(
        accesos_no_api,
        auto_activacion=AUTO_ACTIVACION_SI,
        walkin_nombre=NOMBRE_PASE_UNIT,
        fecha_desde_hasta=fecha_hasta(accesos_no_api, DIAS_VIGENTE),
    )

    estatus = accesos_no_api._status_auto_activacion(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "activo", f"El pase con auto activación quedó {estatus!r}"


@pytest.mark.unit
def test_acompanante_sin_nombre_se_queda_en_proceso(accesos_no_api):
    """
    TB-194: el pase de un acompañante (trae url_padre) hereda la auto
    activación del titular, pero sin nombre debe quedar en 'proceso' hasta
    que lo llenen. Si queda activo, hay un pase vigente sin saber de quién.
    """
    answers = answers_pase(
        accesos_no_api,
        auto_activacion=AUTO_ACTIVACION_SI,
        url_padre=URL_PADRE,
        walkin_nombre="",
        fecha_desde_hasta=fecha_hasta(accesos_no_api, DIAS_VIGENTE),
    )

    estatus = accesos_no_api._status_auto_activacion(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "proceso", f"El acompañante sin nombre quedó {estatus!r}"


@pytest.mark.unit
def test_auto_activacion_no_reactiva_un_pase_vencido(accesos_no_api):
    """
    TB-195: con auto_activacion "sí" y la fecha hasta en el pasado, la fecha
    manda y el pase debe quedar 'vencido'. Si queda activo, entra alguien
    fuera de la vigencia que le dieron.
    """
    answers = answers_pase(
        accesos_no_api,
        auto_activacion=AUTO_ACTIVACION_SI,
        walkin_nombre=NOMBRE_PASE_UNIT,
        fecha_desde_hasta=fecha_hasta(accesos_no_api, DIAS_VENCIDO),
    )

    estatus = accesos_no_api._status_auto_activacion(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "vencido", f"El pase vencido con auto activación quedó {estatus!r}"
