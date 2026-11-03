# coding: utf-8

"""
Registrar Ingreso desde + Nuevo Acceso (do_access) con el payload que manda
el front: vehículo, equipo y comentario agregados por el guardia.
Notion: TB-084 y TB-085.
"""

import copy

import pytest

from .fixtures import *
from ..data.nuevo_acceso_data import (
    LOCATION,
    AREA,
    VEHICULO_NUEVA_VISITA,
    EQUIPO_NUEVA_VISITA,
    COMENTARIO_PASE_NUEVA_VISITA,
    LIMITE_VARIAS_ENTRADAS,
)
from passes.integration.helpers import crear_pase
from entradas_salidas.integration.helpers import ultima_visita, salida_silenciosa, dar_entrada


@pytest.mark.integration
def test_do_access_guarda_vehiculo_equipo_y_comentario(acceso_obj, mock_pase_nueva_visita):
    """
    TB-084: al Registrar Ingreso con un vehículo, un equipo y un comentario,
    la visita debe guardar los tres. Si no, la bitácora no muestra con qué
    entró la persona y el guardia no puede revisarlo a la salida.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nueva_visita)
    pase = acceso_obj.search_access_pass(qr_code=pase_id, location=LOCATION)

    # Mismo payload que arma el front (accesos/page.tsx → registerIncoming).
    data = {
        "comentario_acceso": [],
        "comentario_pase": [COMENTARIO_PASE_NUEVA_VISITA],
        "equipo": [EQUIPO_NUEVA_VISITA],
        "vehiculo": [VEHICULO_NUEVA_VISITA],
        "gafete": {},
        "visita_a": pase.get("visita_a") or [],
        "selected_passes": [],
    }
    res = acceso_obj.do_access(pase_id, LOCATION, AREA, data)

    try:
        assert res.get("status_code") in (200, 201, 202), f"No se registró el ingreso: {res}"

        visita = ultima_visita(acceso_obj, pase_id)
        assert visita["status_visita"] == "entrada"

        placas = {v.get("placas") for v in visita.get("vehiculos") or []}
        assert VEHICULO_NUEVA_VISITA["placas"] in placas, f"La visita no guardó el vehículo: {visita.get('vehiculos')}"

        series = {e.get("numero_serie") for e in visita.get("equipos") or []}
        assert EQUIPO_NUEVA_VISITA["serie"] in series, f"La visita no guardó el equipo: {visita.get('equipos')}"

        comentarios = {c.get("comentario") for c in visita.get("comentarios") or []}
        assert COMENTARIO_PASE_NUEVA_VISITA["comentario_pase"] in comentarios, (
            f"La visita no guardó el comentario: {visita.get('comentarios')}"
        )
    finally:
        salida_silenciosa(acceso_obj, pase_id, LOCATION, AREA)


@pytest.mark.integration
def test_do_access_segundo_ingreso_sin_salida_es_rechazado(acceso_obj, mock_pase_nueva_visita):
    """
    TB-085: con la persona dentro, un segundo Registrar Ingreso del mismo pase
    debe rechazarse ('ya se encuentra dentro') y no crear otra visita. Si no,
    la bitácora queda con dos entradas abiertas y la salida cierra solo una.
    """
    pase = copy.deepcopy(mock_pase_nueva_visita)
    pase["config_limitar_acceso"] = LIMITE_VARIAS_ENTRADAS
    pase_id = crear_pase(acceso_obj, pase)
    entrada = dar_entrada(acceso_obj, pase_id, LOCATION, AREA)

    try:
        with pytest.raises(Exception) as exc_info:
            acceso_obj.do_access(pase_id, LOCATION, AREA, {})
        assert "ya se encuentra dentro" in str(exc_info.value), f"Rechazo inesperado: {exc_info.value}"

        visitas = acceso_obj.get_list_last_user_move(pase_id)
        assert [v["_id"] for v in visitas] == [entrada["_id"]], f"Se creó otra visita: {visitas}"
    finally:
        salida_silenciosa(acceso_obj, pase_id, LOCATION, AREA)
