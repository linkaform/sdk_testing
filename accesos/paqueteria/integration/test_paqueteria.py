# coding: utf-8

"""
Paquetería: recibir un paquete y consultarlo en Pendientes, Entregados y
Todos, y entregarlo (paqueteria.py: nuevo_paquete, get_paquetes,
actualizar_paquete).
Notion: TB-152.
"""

import pytest

from .fixtures import *
from ..data.paqueteria_data import (
    LOCATION,
    AREA,
    ESTATUS_GUARDADO,
)


@pytest.mark.integration
def test_recibir_paquete_para_empleado_lo_muestra_en_pendientes(mock_paquete_nuevo, paquete_guardado):
    """
    TB-152: un paquete recibido desde + Nuevo Paquete para un empleado debe
    aparecer en Pendientes con los datos que capturó el guardia. Si falta
    alguno, el destinatario no sabe que llegó ni dónde está guardado.
    """
    assert paquete_guardado.get("estatus_paqueteria") == ESTATUS_GUARDADO, (
        f"El paquete quedó '{paquete_guardado.get('estatus_paqueteria')}'"
    )
    assert paquete_guardado.get("ubicacion_paqueteria") == LOCATION
    assert paquete_guardado.get("area_paqueteria") == AREA
    for campo in ("quien_recibe_paqueteria", "proveedor", "guardado_en_paqueteria", "fecha_recibido_paqueteria"):
        assert paquete_guardado.get(campo) == mock_paquete_nuevo[campo], (
            f"'{campo}' quedó {paquete_guardado.get(campo)!r}, se mandó {mock_paquete_nuevo[campo]!r}"
        )
