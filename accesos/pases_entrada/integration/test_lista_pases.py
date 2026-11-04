# coding: utf-8

"""
Lista de pases (get_my_pases): pestañas Activos, Por autorizar, En Proceso y
Todos de la pantalla Pases de Entrada.
Notion: TB-111 a TB-113.
"""

import copy

import pytest

from .fixtures import *
from ..data.pases_entrada_data import (
    TAB_EN_PROCESO,
    TAB_ACTIVOS,
    ESTATUS_PROCESO,
    ESTATUS_ACTIVO,
    PASE_COMPLETAR,
    TAB_POR_AUTORIZAR,
    ESTATUS_POR_AUTORIZAR,
    LIMITE_LISTA,
)
from passes.integration.helpers import crear_pase


@pytest.mark.integration
def test_pase_nuevo_de_web_aparece_en_proceso_y_no_en_activos(acceso_obj, mock_pase_nuevo):
    """
    TB-111: un pase creado desde + Nuevo Pase sin auto activación y sin
    requisitos de foto o identificación queda en 'proceso'. Debe aparecer en
    la pestaña En Proceso y no en Activos; si sale en Activos, el guardia lo
    trata como listo aunque el visitante no lo ha completado.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nuevo)
    nombre = mock_pase_nuevo["nombre"]

    en_proceso = acceso_obj.get_my_pases(tab_status=TAB_EN_PROCESO, search_name=nombre, limit=LIMITE_LISTA)
    pases_en_proceso = {p["_id"]: p for p in en_proceso["records"]}
    assert pase_id in pases_en_proceso, "El pase nuevo no aparece en En Proceso"
    assert pases_en_proceso[pase_id].get("estatus") == ESTATUS_PROCESO, (
        f"El pase quedó '{pases_en_proceso[pase_id].get('estatus')}'"
    )

    activos = acceso_obj.get_my_pases(tab_status=TAB_ACTIVOS, search_name=nombre, limit=LIMITE_LISTA)
    assert pase_id not in {p["_id"] for p in activos["records"]}, "El pase en proceso aparece en Activos"


@pytest.mark.integration
def test_completar_pase_lo_pasa_de_en_proceso_a_activos(acceso_obj, mock_pase_nuevo):
    """
    TB-112: cuando el visitante completa su pase en pase-update (foto,
    identificación y aviso de privacidad, con el payload del modal de
    confirmación), el pase debe pasar a 'activo': aparecer en Activos y salir
    de En Proceso. Si se queda en proceso, el visitante no puede entrar
    aunque ya cumplió los requisitos.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nuevo)
    nombre = mock_pase_nuevo["nombre"]

    completar = copy.deepcopy(PASE_COMPLETAR)
    completar.update({
        "nombre": nombre,
        "email": mock_pase_nuevo["email"],
        "telefono_pase": mock_pase_nuevo["telefono"],
    })
    res = acceso_obj.update_pass(completar, pase_id)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo completar el pase: {res}"

    activos = acceso_obj.get_my_pases(tab_status=TAB_ACTIVOS, search_name=nombre, limit=LIMITE_LISTA)
    pases_activos = {p["_id"]: p for p in activos["records"]}
    assert pase_id in pases_activos, "El pase completado no aparece en Activos"
    assert pases_activos[pase_id].get("estatus") == ESTATUS_ACTIVO, (
        f"El pase completado quedó '{pases_activos[pase_id].get('estatus')}'"
    )

    en_proceso = acceso_obj.get_my_pases(tab_status=TAB_EN_PROCESO, search_name=nombre, limit=LIMITE_LISTA)
    assert pase_id not in {p["_id"] for p in en_proceso["records"]}, "El pase completado sigue en En Proceso"


@pytest.mark.integration
def test_pase_de_auto_registro_completo_cae_en_por_autorizar(acceso_obj, mock_pase_auto_registro):
    """
    TB-113: un visitante que se registra solo (auto registro) con foto e
    identificación deja un pase completo pero sin autorizar. Debe aparecer
    en la pestaña Por autorizar y no en Activos; si sale en Activos, entra
    sin que nadie lo haya autorizado.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_auto_registro)
    nombre = mock_pase_auto_registro["nombre"]

    por_autorizar = acceso_obj.get_my_pases(tab_status=TAB_POR_AUTORIZAR, search_name=nombre, limit=LIMITE_LISTA)
    pases_por_autorizar = {p["_id"]: p for p in por_autorizar["records"]}
    assert pase_id in pases_por_autorizar, "El pase de auto registro no aparece en Por autorizar"
    assert pases_por_autorizar[pase_id].get("estatus") == ESTATUS_POR_AUTORIZAR, (
        f"El pase de auto registro quedó '{pases_por_autorizar[pase_id].get('estatus')}'"
    )

    activos = acceso_obj.get_my_pases(tab_status=TAB_ACTIVOS, search_name=nombre, limit=LIMITE_LISTA)
    assert pase_id not in {p["_id"] for p in activos["records"]}, "El pase sin autorizar aparece en Activos"
