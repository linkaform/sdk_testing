# coding: utf-8

import copy
import uuid
from datetime import datetime

import pytest
import pytz

from ..data.fallas_data import (
    LOCATION,
    FALLA_NUEVA,
    COMENTARIO_FALLA,
    ESTATUS_ABIERTO,
)
from .helpers import falla_de_la_lista


@pytest.fixture
def acceso_obj(accesos_api):
    """Cliente de Accesos con API Key y el usuario de la cuenta activa (ver conftest)."""
    return accesos_api


@pytest.fixture
def mock_falla_nueva(acceso_obj):
    """
    Falla de + Nueva Falla con un comentario que solo existe en esta corrida.
    Tipo de falla y objeto afectado de la falla más reciente de la ubicación;
    reporta y responsable = el empleado del usuario.
    """
    existentes = [
        f for f in acceso_obj.get_list_fallas([LOCATION], "")
        if f.get("falla") and f.get("falla_objeto_afectado")
    ]
    if not existentes:
        pytest.skip(f"No hay fallas en {LOCATION} de donde tomar el tipo de falla y el objeto afectado")
    empleado = acceso_obj.get_employee_data(email=acceso_obj.user.get("email"), get_one=True)
    nombre = empleado.get("worker_name")
    if not nombre:
        pytest.skip("El usuario de la cuenta no tiene empleado para reportar la falla")

    falla = copy.deepcopy(FALLA_NUEVA)
    falla.update({
        "falla": existentes[0]["falla"],
        "falla_objeto_afectado": existentes[0]["falla_objeto_afectado"],
        "falla_reporta_nombre": nombre,
        "falla_responsable_solucionar_nombre": nombre,
        "falla_comentarios": f"{COMENTARIO_FALLA} {uuid.uuid4().hex[:8]}",
        "falla_fecha_hora": datetime.now(pytz.timezone(acceso_obj.user["timezone"])).strftime("%Y-%m-%d %H:%M:%S"),
    })
    return falla


@pytest.fixture
def falla_abierta(acceso_obj, mock_falla_nueva):
    """Falla recién creada con el payload de + Nueva Falla, tal como sale en Abiertas."""
    res = acceso_obj.create_failure(mock_falla_nueva)
    assert res.get("status_code") in (200, 201, 202), f"No se pudo crear la falla: {res}"

    falla = falla_de_la_lista(acceso_obj, mock_falla_nueva["falla_comentarios"], ESTATUS_ABIERTO)
    assert falla, "La falla nueva no aparece en Abiertas"
    return falla
