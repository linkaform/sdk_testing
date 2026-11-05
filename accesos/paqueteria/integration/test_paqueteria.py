# coding: utf-8

"""
Paquetería: recibir un paquete y consultarlo en Pendientes, Entregados y
Todos, y entregarlo (paqueteria.py: nuevo_paquete, get_paquetes,
actualizar_paquete).
Notion: TB-152 y TB-153.
"""

import copy

import pytest

from .fixtures import *
from .helpers import paquete_de_la_lista
from ..data.paqueteria_data import (
    LOCATION,
    AREA,
    DESTINATARIO_EXTERNO,
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


@pytest.mark.integration
def test_recibir_paquete_para_externo_lo_muestra_con_su_nombre(acceso_obj, mock_paquete_nuevo):
    """
    TB-153: un paquete para alguien que no es empleado (destinatario "Otro")
    debe aparecer en Pendientes con el nombre de esa persona como
    destinatario. Si sale vacío, el guardia no sabe a quién entregarlo.
    """
    paquete = copy.deepcopy(mock_paquete_nuevo)
    paquete.pop("quien_recibe_paqueteria")
    paquete["quien_recibe_otro"] = DESTINATARIO_EXTERNO
    res = acceso_obj.create_paquete(paquete)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo recibir el paquete: {res}"

    guardado = paquete_de_la_lista(acceso_obj, paquete["descripcion_paqueteria"], ESTATUS_GUARDADO)
    assert guardado, "El paquete para el destinatario externo no aparece en Pendientes"
    assert guardado.get("quien_recibe_paqueteria") == DESTINATARIO_EXTERNO, (
        f"El destinatario quedó {guardado.get('quien_recibe_paqueteria')!r}"
    )
