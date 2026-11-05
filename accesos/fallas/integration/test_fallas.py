# coding: utf-8

"""
Fallas de Seguridad: crear una falla y consultarla en Abiertas, Cerradas y
Todos, cerrarla y editarla (fallas.py: new_failure, get_failures,
update_failure).
Notion: TB-138.
"""

import pytest

from .fixtures import *
from .helpers import falla_de_la_lista
from ..data.fallas_data import (
    LOCATION,
    AREA,
    ESTATUS_ABIERTO,
)


@pytest.mark.integration
def test_crear_falla_la_muestra_en_abiertas(mock_falla_nueva, falla_abierta):
    """
    TB-138: una falla creada desde + Nueva Falla debe aparecer en Abiertas
    con los datos que capturó el guardia. Si falta alguno, quien la atiende
    no sabe qué falló, dónde ni a quién le toca.
    """
    assert falla_abierta.get("falla_estatus") == ESTATUS_ABIERTO, f"La falla quedó '{falla_abierta.get('falla_estatus')}'"
    assert falla_abierta.get("falla_ubicacion") == LOCATION
    assert falla_abierta.get("falla_caseta") == AREA
    for campo in ("falla", "falla_objeto_afectado", "falla_reporta_nombre", "falla_responsable_solucionar_nombre", "falla_fecha_hora"):
        assert falla_abierta.get(campo) == mock_falla_nueva[campo], (
            f"'{campo}' quedó {falla_abierta.get(campo)!r}, se mandó {mock_falla_nueva[campo]!r}"
        )
