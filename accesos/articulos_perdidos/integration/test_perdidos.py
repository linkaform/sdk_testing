# coding: utf-8

"""
Artículos Perdidos: registrar un artículo y consultarlo en Pendientes,
Entregados y Todos; entregarlo o donarlo (articulos_perdidos.py:
nuevo_articulo, get_articles, update_article).
Notion: TB-146.
"""

import pytest

from .fixtures import *
from .helpers import articulo_de_la_lista
from ..data.perdidos_data import (
    LOCATION,
    AREA,
    ESTATUS_PENDIENTE,
)


@pytest.mark.integration
def test_registrar_articulo_lo_muestra_en_pendientes(mock_articulo_nuevo, articulo_pendiente):
    """
    TB-146: un artículo registrado desde + Nuevo Artículo debe aparecer en
    Pendientes con los datos que capturó el guardia. Si falta alguno, quien
    lo reclama no puede identificarlo.
    """
    assert articulo_pendiente.get("estatus_perdido") == ESTATUS_PENDIENTE, (
        f"El artículo quedó '{articulo_pendiente.get('estatus_perdido')}'"
    )
    assert articulo_pendiente.get("ubicacion_perdido") == LOCATION
    assert articulo_pendiente.get("area_perdido") == AREA
    for campo in ("tipo_articulo_perdido", "articulo_seleccion", "color_perdido", "descripcion", "date_hallazgo_perdido"):
        assert articulo_pendiente.get(campo) == mock_articulo_nuevo[campo], (
            f"'{campo}' quedó {articulo_pendiente.get(campo)!r}, se mandó {mock_articulo_nuevo[campo]!r}"
        )
