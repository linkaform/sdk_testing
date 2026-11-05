# coding: utf-8

import copy
import uuid
from datetime import datetime

import pytest
import pytz

from ..data.paqueteria_data import (
    LOCATION,
    PAQUETE_NUEVO,
    DESCRIPCION_PAQUETE,
    ESTATUS_GUARDADO,
)
from .helpers import paquete_de_la_lista


@pytest.fixture
def acceso_obj(accesos_api):
    """Cliente de Accesos con API Key y el usuario de la cuenta activa (ver conftest)."""
    return accesos_api


@pytest.fixture
def mock_paquete_nuevo(acceso_obj):
    """
    Paquete de + Nuevo Paquete para el empleado del usuario, con una
    descripción que solo existe en esta corrida. Proveedor y locker del
    paquete más reciente de la ubicación que los tenga.
    """
    existentes = [
        p for p in acceso_obj.get_paquetes(LOCATION, "")
        if p.get("proveedor") and p.get("guardado_en_paqueteria")
    ]
    if not existentes:
        pytest.skip(f"No hay paquetes en {LOCATION} de donde tomar el proveedor y el locker")
    empleado = acceso_obj.get_employee_data(email=acceso_obj.user.get("email"), get_one=True)
    nombre = empleado.get("worker_name")
    if not nombre:
        pytest.skip("El usuario de la cuenta no tiene empleado para recibir el paquete")

    paquete = copy.deepcopy(PAQUETE_NUEVO)
    paquete.update({
        "descripcion_paqueteria": f"{DESCRIPCION_PAQUETE} {uuid.uuid4().hex[:8]}",
        "quien_recibe_paqueteria": nombre,
        "proveedor": existentes[0]["proveedor"],
        "guardado_en_paqueteria": existentes[0]["guardado_en_paqueteria"],
        "fecha_recibido_paqueteria": datetime.now(pytz.timezone(acceso_obj.user["timezone"])).strftime("%Y-%m-%d %H:%M:%S"),
    })
    return paquete


@pytest.fixture
def paquete_guardado(acceso_obj, mock_paquete_nuevo):
    """Paquete recién recibido con el payload de + Nuevo Paquete, tal como sale en Pendientes."""
    res = acceso_obj.create_paquete(mock_paquete_nuevo)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo recibir el paquete: {res}"

    paquete = paquete_de_la_lista(acceso_obj, mock_paquete_nuevo["descripcion_paqueteria"], ESTATUS_GUARDADO)
    assert paquete, "El paquete nuevo no aparece en Pendientes"
    return paquete
