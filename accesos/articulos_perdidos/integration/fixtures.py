# coding: utf-8

import copy
import uuid
from datetime import datetime

import pytest
import pytz

from ..data.perdidos_data import (
    LOCATION,
    ARTICULO_NUEVO,
    NOMBRE_ARTICULO,
    ESTATUS_PENDIENTE,
)
from .helpers import articulo_de_la_lista


@pytest.fixture
def acceso_obj(accesos_api):
    """Cliente de Accesos con API Key y el usuario de la cuenta activa (ver conftest)."""
    return accesos_api


@pytest.fixture
def mock_articulo_nuevo(acceso_obj):
    """
    Artículo de + Nuevo Artículo con un nombre que solo existe en esta
    corrida. Tipo de artículo y artículo del registro más reciente de la
    ubicación que los tenga.
    """
    existentes = [
        a for a in acceso_obj.get_list_article_lost(LOCATION, "")
        if a.get("tipo_articulo_perdido") and a.get("articulo_seleccion")
    ]
    if not existentes:
        pytest.skip(f"No hay artículos perdidos en {LOCATION} de donde tomar el tipo de artículo")

    articulo = copy.deepcopy(ARTICULO_NUEVO)
    articulo.update({
        "articulo_perdido": f"{NOMBRE_ARTICULO} {uuid.uuid4().hex[:8]}",
        "tipo_articulo_perdido": existentes[0]["tipo_articulo_perdido"],
        "articulo_seleccion": existentes[0]["articulo_seleccion"],
        "date_hallazgo_perdido": datetime.now(pytz.timezone(acceso_obj.user["timezone"])).strftime("%Y-%m-%d %H:%M:%S"),
    })
    return articulo


@pytest.fixture
def articulo_pendiente(acceso_obj, mock_articulo_nuevo):
    """Artículo recién registrado con el payload de + Nuevo Artículo, tal como sale en Pendientes."""
    res = acceso_obj.create_article_lost(mock_articulo_nuevo)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo registrar el artículo: {res}"

    articulo = articulo_de_la_lista(acceso_obj, mock_articulo_nuevo["articulo_perdido"], ESTATUS_PENDIENTE)
    assert articulo, "El artículo nuevo no aparece en Pendientes"
    return articulo
