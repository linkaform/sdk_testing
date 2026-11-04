# coding: utf-8

"""
Lista de pases (get_my_pases): pestañas Activos, Por autorizar, En Proceso y
Todos de la pantalla Pases de Entrada.
Notion: TB-111.
"""

import pytest

from .fixtures import *
from ..data.pases_entrada_data import (
    TAB_EN_PROCESO,
    TAB_ACTIVOS,
    ESTATUS_PROCESO,
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
