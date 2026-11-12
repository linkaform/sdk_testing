# coding: utf-8

"""
Estatus del pase (access_pass_set_status): activo, por autorizar, en proceso
o vencido según lo que trae el pase y lo que pide la ubicación. Función
directa, sin preprod.
Notion: TB-197 a TB-201.
"""

import pytest

from .helpers import answers_pase, campos_pase_completo
from ..data.pases_entrada_data import DIAS_VIGENTE, REQUIERE_FOTO_E_IDENTIFICACION, SIN_REQUERIMIENTOS


@pytest.mark.unit
def test_pase_completo_y_autorizado_queda_activo(accesos_no_api):
    """
    TB-197: con nombre, foto e identificación válidas (la ubicación las
    pide), fecha vigente, a quién visita y quién lo autorizó, el pase debe
    quedar 'activo'. Si no, un pase listo se queda esperando sin razón.
    """
    answers = answers_pase(accesos_no_api, **campos_pase_completo(accesos_no_api, DIAS_VIGENTE))

    estatus = accesos_no_api.access_pass_set_status(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "activo", f"El pase completo y autorizado quedó {estatus!r}"


@pytest.mark.unit
def test_pase_completo_sin_autorizar_queda_por_autorizar(accesos_no_api):
    """
    TB-198: con todo completo pero sin quién lo autorizó (como un auto
    registro), el pase debe quedar 'por_autorizar'. Si queda activo, entra
    alguien que nadie aprobó.
    """
    campos = campos_pase_completo(accesos_no_api, DIAS_VIGENTE)
    campos.pop("catalago_autorizado_por")
    answers = answers_pase(accesos_no_api, **campos)

    estatus = accesos_no_api.access_pass_set_status(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "por_autorizar", f"El pase sin autorizar quedó {estatus!r}"


@pytest.mark.unit
def test_pase_sin_la_foto_que_pide_la_ubicacion_queda_en_proceso(accesos_no_api):
    """
    TB-199: con todo completo y autorizado pero sin foto, en una ubicación
    que pide fotografía, el pase debe quedar en 'proceso' hasta que el
    visitante la suba. Si queda activo, entra sin la foto que la ubicación
    exige.
    """
    campos = campos_pase_completo(accesos_no_api, DIAS_VIGENTE)
    campos.pop("walkin_fotografia")
    answers = answers_pase(accesos_no_api, **campos)

    estatus = accesos_no_api.access_pass_set_status(answers, requerimientos=REQUIERE_FOTO_E_IDENTIFICACION)
    assert estatus == "proceso", f"El pase sin foto quedó {estatus!r}"


@pytest.mark.unit
def test_ubicacion_sin_requerimientos_deja_activo_sin_foto_ni_identificacion(accesos_no_api):
    """
    TB-200: si la ubicación no pide foto ni identificación, un pase sin ellas
    pero con nombre, fecha vigente, a quién visita y autorizado debe quedar
    'activo'. Si queda en proceso, se queda ahí para siempre porque el link
    no le pide nada al visitante.
    """
    campos = campos_pase_completo(accesos_no_api, DIAS_VIGENTE)
    campos.pop("walkin_fotografia")
    campos.pop("walkin_identificacion")
    answers = answers_pase(accesos_no_api, **campos)

    estatus = accesos_no_api.access_pass_set_status(answers, requerimientos=SIN_REQUERIMIENTOS)
    assert estatus == "activo", f"El pase sin requisitos quedó {estatus!r}"
