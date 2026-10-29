# coding: utf-8

import copy
import pytest

from passes.integration.helpers import fecha_str, crear_pase
from entradas_salidas.integration.helpers import dar_entrada, salida_silenciosa
from ..data.nuevo_acceso_data import PASE_NUEVA_VISITA, LOCATION, AREA


@pytest.fixture
def acceso_obj(accesos_api):
    """Cliente de Accesos con API Key y el usuario de la cuenta activa (ver conftest)."""
    return accesos_api


@pytest.fixture
def mock_pase_nueva_visita(acceso_obj):
    """
    Pase de Nueva Visita para hoy, con el primer anfitrión que ofrece el modal
    en la ubicación (assets_access_pass), igual que lo elegiría el guardia.
    """
    anfitriones = acceso_obj.assets_access_pass(LOCATION)["Visita_a"]
    assert anfitriones, f"{LOCATION} no tiene anfitriones para el pase de Nueva Visita"

    hoy = fecha_str(0)[:10]
    pase = copy.deepcopy(PASE_NUEVA_VISITA)
    pase["visita_a"] = anfitriones[0]
    pase["fecha_desde_visita"] = f"{hoy} 00:00:00"
    pase["fecha_desde_hasta"] = f"{hoy} 23:59:00"
    return pase


@pytest.fixture
def pase_nueva_visita_dentro(acceso_obj, mock_pase_nueva_visita):
    """
    Pase de Nueva Visita con la entrada ya registrada en LOCATION/AREA.
    Regresa (pase_id, registro_entrada). Al terminar intenta dar la salida
    para no dejar a la persona "dentro" en preprod.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nueva_visita)
    registro = dar_entrada(acceso_obj, pase_id, LOCATION, AREA)
    yield pase_id, registro
    salida_silenciosa(acceso_obj, pase_id, LOCATION, AREA)
