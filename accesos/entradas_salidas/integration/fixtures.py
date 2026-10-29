# coding: utf-8

import copy
import pytest

from passes.integration.helpers import fecha_str
from ..data.bitacora_data import (
    PASE_BITACORA, LOCATION, AREA, PASE_BITACORA_OTRA_UBICACION, OTRA_LOCATION, OTRA_AREA,
)
from .helpers import crear_pase, completar_pase_activo, dar_entrada, salida_silenciosa


@pytest.fixture
def acceso_obj(accesos_api):
    """Cliente de Accesos con API Key y el usuario de la cuenta activa (ver conftest)."""
    return accesos_api


@pytest.fixture
def mock_pase_bitacora():
    """Pase vigente desde hoy y por 7 días, listo para crearse."""
    pase = copy.deepcopy(PASE_BITACORA)
    pase["fecha_desde_visita"] = fecha_str(0)
    pase["fecha_desde_hasta"] = fecha_str(7)
    return pase


@pytest.fixture
def pase_activo(acceso_obj, mock_pase_bitacora):
    """Folio de un pase creado y completado (estatus 'activo'), sin entrada."""
    folio = crear_pase(acceso_obj, mock_pase_bitacora)
    completar_pase_activo(acceso_obj, folio)
    return folio


@pytest.fixture
def pase_dentro(acceso_obj, pase_activo):
    """
    Pase activo con la entrada ya registrada en LOCATION/AREA.
    Regresa (folio, registro_entrada). Al terminar intenta dar la salida
    para no dejar a la persona "dentro" en preprod.
    """
    registro = dar_entrada(acceso_obj, pase_activo, LOCATION, AREA)
    yield pase_activo, registro
    salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)


@pytest.fixture
def pase_dentro_otra_ubicacion(acceso_obj):
    """
    Pase activo con la entrada registrada en OTRA_LOCATION/OTRA_AREA.
    Regresa (folio, registro_entrada) y al terminar intenta dar la salida.
    """
    pase = copy.deepcopy(PASE_BITACORA_OTRA_UBICACION)
    pase["fecha_desde_visita"] = fecha_str(0)
    pase["fecha_desde_hasta"] = fecha_str(7)
    folio = crear_pase(acceso_obj, pase)
    completar_pase_activo(acceso_obj, folio)
    registro = dar_entrada(acceso_obj, folio, OTRA_LOCATION, OTRA_AREA)
    yield folio, registro
    salida_silenciosa(acceso_obj, folio, OTRA_LOCATION, OTRA_AREA)
