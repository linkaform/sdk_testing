# coding: utf-8

import pytest

from ..data.notas_data import (
    LOCATION,
    AREA,
    NOTA_NUEVA,
    TODAS_LAS_AREAS,
    ESTATUS_ABIERTO,
    LIMITE_LISTA,
)


@pytest.fixture
def acceso_obj(accesos_api):
    """Cliente de Accesos con API Key y el usuario de la cuenta activa (ver conftest)."""
    return accesos_api


@pytest.fixture
def nota_abierta(acceso_obj):
    """
    Nota recién creada con el payload de + Nueva Nota, tal como sale en
    Pendientes (con _id y folio, que es lo que usan editar y cerrar).
    """
    res = acceso_obj.create_note(LOCATION, AREA, NOTA_NUEVA)
    nota_id = (res.get("json") or {}).get("id")
    assert res.get("status_code") in (200, 201, 202) and nota_id, f"No se pudo crear la nota: {res}"

    pendientes = acceso_obj.get_list_notes(LOCATION, TODAS_LAS_AREAS, status=ESTATUS_ABIERTO, limit=LIMITE_LISTA)
    notas = {n["_id"]: n for n in pendientes["records"]}
    assert nota_id in notas, "La nota nueva no aparece en Pendientes"
    return notas[nota_id]
