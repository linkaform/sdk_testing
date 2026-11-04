# coding: utf-8

import copy
import pytest

from passes.integration.helpers import fecha_str
from ..data.pases_entrada_data import PASE_NUEVO


@pytest.fixture
def acceso_obj(accesos_api):
    """Cliente de Accesos con API Key y el usuario de la cuenta activa (ver conftest)."""
    return accesos_api


@pytest.fixture
def mock_pase_nuevo():
    """Pase de + Nuevo Pase vigente desde hoy y por 7 días, listo para crearse."""
    pase = copy.deepcopy(PASE_NUEVO)
    pase["fecha_desde_visita"] = fecha_str(0)
    pase["fecha_desde_hasta"] = fecha_str(7)
    return pase
