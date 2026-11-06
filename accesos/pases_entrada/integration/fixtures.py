# coding: utf-8

import copy
import uuid
import pytest

from passes.integration.helpers import fecha_str, crear_pase
from ..data.pases_entrada_data import (
    PASE_NUEVO,
    PASE_AUTO_REGISTRO,
    PASE_COMPLETAR,
    PASE_AUTO_ACTIVACION,
    PASE_SIN_REQUISITOS,
    PASE_PIDE_FOTO_E_IDENTIFICACION,
    PASES_PARA_PAGINAR,
    ACOMPANANTES_PASE,
)


def _vigente_7_dias(pase):
    """Copia del pase vigente desde hoy y por 7 días."""
    pase = copy.deepcopy(pase)
    pase["fecha_desde_visita"] = fecha_str(0)
    pase["fecha_desde_hasta"] = fecha_str(7)
    return pase


@pytest.fixture
def acceso_obj(accesos_api):
    """Cliente de Accesos con API Key y el usuario de la cuenta activa (ver conftest)."""
    return accesos_api


@pytest.fixture
def mock_pase_nuevo():
    """Pase de + Nuevo Pase vigente desde hoy y por 7 días, listo para crearse."""
    return _vigente_7_dias(PASE_NUEVO)


@pytest.fixture
def mock_pase_con_acompanantes(mock_pase_nuevo):
    """+ Nuevo Pase con dos acompañantes, listo para crearse."""
    mock_pase_nuevo["acompanantes"] = len(ACOMPANANTES_PASE)
    mock_pase_nuevo["acompanantes_grupo"] = copy.deepcopy(ACOMPANANTES_PASE)
    return mock_pase_nuevo


@pytest.fixture
def mock_pase_auto_activacion():
    """+ Nuevo Pase con "Activar pase por defecto" prendido, sin foto ni identificación."""
    return _vigente_7_dias(PASE_AUTO_ACTIVACION)


@pytest.fixture
def mock_pase_sin_requisitos():
    """+ Nuevo Pase sin auto activación y con foto e identificación apagadas por el admin."""
    return _vigente_7_dias(PASE_SIN_REQUISITOS)


@pytest.fixture
def mock_pase_pide_foto_e_identificacion():
    """+ Nuevo Pase sin auto activación que pide foto e identificación, sin traerlas."""
    return _vigente_7_dias(PASE_PIDE_FOTO_E_IDENTIFICACION)


@pytest.fixture
def mock_pase_auto_registro(acceso_obj):
    """Pase de auto registro con el usuario de la cuenta como anfitrión (visita_a por email)."""
    pase = copy.deepcopy(PASE_AUTO_REGISTRO)
    pase["visita_a"] = {"nombre": "", "email": acceso_obj.user["email"], "telefono": ""}
    return pase


@pytest.fixture
def pase_completado(acceso_obj, mock_pase_nuevo):
    """
    Pase de + Nuevo Pase ya completado por el visitante (payload del modal de
    confirmación de pase-update), o sea activo. Regresa su id.
    """
    pase_id = crear_pase(acceso_obj, copy.deepcopy(mock_pase_nuevo))
    completar = copy.deepcopy(PASE_COMPLETAR)
    completar.update({
        "nombre": mock_pase_nuevo["nombre"],
        "email": mock_pase_nuevo["email"],
        "telefono_pase": mock_pase_nuevo["telefono"],
    })
    res = acceso_obj.update_pass(completar, pase_id)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo completar el pase: {res}"
    return pase_id


@pytest.fixture
def mock_pase_nombre_unico(mock_pase_nuevo):
    """Pase de + Nuevo Pase con un nombre que solo existe en esta corrida."""
    mock_pase_nuevo["nombre"] = f"{mock_pase_nuevo['nombre']} {uuid.uuid4().hex[:8]}"
    return mock_pase_nuevo


@pytest.fixture
def pases_para_paginar(acceso_obj, mock_pase_nombre_unico):
    """
    Crea PASES_PARA_PAGINAR pases con el mismo nombre único. Regresa el nombre
    y los ids creados.
    """
    ids = {crear_pase(acceso_obj, copy.deepcopy(mock_pase_nombre_unico)) for _ in range(PASES_PARA_PAGINAR)}
    return mock_pase_nombre_unico["nombre"], ids
