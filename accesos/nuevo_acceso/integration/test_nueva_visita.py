# coding: utf-8

"""
Pase creado desde el modal "Nueva Visita" (+ Nuevo Acceso): create_access_pass
con created_from='nueva_visita' y, con el id que regresa, search_access_pass.
Notion: TB-080.
"""

import pytest

from .fixtures import *
from ..data.nuevo_acceso_data import LOCATION
from passes.integration.helpers import crear_pase


@pytest.mark.integration
def test_nueva_visita_crea_pase_activo_y_se_encuentra(acceso_obj, mock_pase_nueva_visita):
    """
    TB-080: al guardar Nueva Visita con foto e identificación, el pase debe
    quedar activo, y la búsqueda con el id que regresa (lo que hace el front
    después de guardar) debe traer ese mismo pase con el nombre y la
    ubicación enviados. Si no, el guardia no puede registrar el ingreso.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nueva_visita)

    pase = acceso_obj.search_access_pass(qr_code=pase_id, location=LOCATION)

    assert pase.get("_id") == pase_id, f"La búsqueda regresó otro pase: {pase.get('_id')}"
    assert pase.get("estatus") == "activo", f"El pase de Nueva Visita quedó '{pase.get('estatus')}'"
    assert pase.get("nombre") == mock_pase_nueva_visita["nombre"]
    assert LOCATION in (pase.get("ubicacion") or []), f"El pase no tiene la ubicación {LOCATION}: {pase.get('ubicacion')}"
