# coding: utf-8

"""
Datos que carga el modal "Nueva Visita" (+ Nuevo Acceso) al abrirse:
assets_access_pass regresa las áreas, los anfitriones, los perfiles y los
requerimientos de la ubicación de la caseta.
Notion: TB-078.
"""

import pytest

from .fixtures import *
from ..data.nuevo_acceso_data import LOCATION, AREA, LLAVES_ASSETS


@pytest.mark.integration
def test_assets_access_pass_trae_datos_de_la_ubicacion(acceso_obj):
    """
    TB-078: al abrir Nueva Visita, assets_access_pass debe regresar las
    llaves que usa el modal, todas como listas, con las áreas y los
    anfitriones de la ubicación. Si faltan, el guardia no puede elegir a
    quién visita ni el perfil del pase.
    """
    assets = acceso_obj.assets_access_pass(LOCATION)

    assert set(assets) == LLAVES_ASSETS, f"Llaves inesperadas: {sorted(assets)}"
    for llave in LLAVES_ASSETS:
        assert isinstance(assets[llave], list), f"'{llave}' no es lista: {assets[llave]!r}"

    assert AREA in assets["Areas"], f"La caseta {AREA} no está en las áreas de {LOCATION}: {assets['Areas']}"
    assert assets["Visita_a"], f"{LOCATION} no tiene anfitriones para elegir en Visita a"
