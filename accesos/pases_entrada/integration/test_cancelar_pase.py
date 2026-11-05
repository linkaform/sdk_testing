# coding: utf-8

"""
Cancelar un pase desde su detalle (botón "Cancelar pase" de view-pass-modal →
update_pass con status_pase 'cancelado').
Notion: TB-120.
"""

import pytest

from .fixtures import *
from ..data.pases_entrada_data import (
    TAB_ACTIVOS,
    TAB_TODOS,
    LIMITE_LISTA,
    CANCELAR_PASE,
    ESTATUS_CANCELADO,
    PASE_NUEVO,
)


@pytest.mark.integration
def test_cancelar_pase_lo_saca_de_activos(acceso_obj, pase_completado):
    """
    TB-120: un pase activo cancelado desde su detalle debe quedar
    'cancelado', salir de Activos y seguir en Todos con ese estatus. Si
    sigue en Activos, el visitante puede entrar con un pase cancelado.
    """
    res = acceso_obj.update_pass(dict(CANCELAR_PASE), pase_completado)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo cancelar el pase: {res}"

    estatus = acceso_obj.get_detail_access_pass(pase_completado).get("estatus")
    assert estatus == ESTATUS_CANCELADO, f"El pase cancelado quedó '{estatus}'"

    nombre = PASE_NUEVO["nombre"]
    activos = acceso_obj.get_my_pases(tab_status=TAB_ACTIVOS, search_name=nombre, limit=LIMITE_LISTA)
    assert pase_completado not in {p["_id"] for p in activos["records"]}, "El pase cancelado sigue en Activos"

    todos = acceso_obj.get_my_pases(tab_status=TAB_TODOS, search_name=nombre, limit=LIMITE_LISTA)
    pases = {p["_id"]: p for p in todos["records"]}
    assert pase_completado in pases, "El pase cancelado no aparece en Todos"
    assert pases[pase_completado].get("estatus") == ESTATUS_CANCELADO
