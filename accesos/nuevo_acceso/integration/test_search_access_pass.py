# coding: utf-8

"""
Búsqueda del pase en + Nuevo Acceso (search_access_pass): lo que el front usa
para mostrar el pase y decidir si el botón es Registrar Ingreso o Registrar
Salida.
Notion: TB-081.
"""

import pytest

from .fixtures import *
from ..data.nuevo_acceso_data import LOCATION
from passes.integration.helpers import crear_pase


@pytest.mark.integration
def test_search_access_pass_pase_nuevo_indica_entrada(acceso_obj, mock_pase_nueva_visita):
    """
    TB-081: un pase recién creado, sin visitas, debe indicar tipo_movimiento
    'Entrada', sin últimos accesos y con 0 entradas. Con 'Entrada' el front
    muestra Registrar Ingreso; si dijera 'Salida', el guardia no podría
    darle entrada.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nueva_visita)

    pase = acceso_obj.search_access_pass(qr_code=pase_id, location=LOCATION)

    assert pase.get("tipo_movimiento") == "Entrada", f"Un pase nuevo indica '{pase.get('tipo_movimiento')}'"
    assert pase.get("ultimo_acceso") == [], f"Un pase nuevo trae últimos accesos: {pase.get('ultimo_acceso')}"
    assert int(pase.get("total_entradas")) == 0, f"Un pase nuevo trae {pase.get('total_entradas')} entradas"
