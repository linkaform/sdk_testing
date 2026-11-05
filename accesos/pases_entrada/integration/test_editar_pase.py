# coding: utf-8

"""
Editar el pase completo desde la tabla de pases (Editar → update-full-pass.tsx
→ add-pass-modal-update.tsx → update_full_pass).
Notion: TB-121.
"""

import pytest

from .fixtures import *
from .helpers import pase_de_la_lista, payload_editar_pase
from ..data.pases_entrada_data import (
    EDICION_NOMBRE_SUFIJO,
    EDICION_EMPRESA,
    EDICION_DIAS_DESDE,
    EDICION_DIAS_HASTA,
    EDICION_HORA_HASTA,
)
from passes.integration.helpers import crear_pase, fecha_str


@pytest.mark.integration
def test_editar_pase_completo_guarda_los_cambios(acceso_obj, mock_pase_nuevo):
    """
    TB-121: al editar un pase y cambiar nombre, empresa y fechas, la lista
    debe mostrar los valores nuevos. No basta con que update_full_pass
    responda 2xx: si no los guarda, el guardia ve el pase con los datos
    viejos y el visitante entra con fechas que ya no son las acordadas.
    """
    pase_id = crear_pase(acceso_obj, mock_pase_nuevo)
    pase = pase_de_la_lista(acceso_obj, pase_id, mock_pase_nuevo["nombre"])
    assert pase, f"El pase {pase_id} no aparece en la lista para editarlo"

    cambios = {
        "nombre": mock_pase_nuevo["nombre"] + EDICION_NOMBRE_SUFIJO,
        "empresa": EDICION_EMPRESA,
        "fecha_desde_visita": fecha_str(EDICION_DIAS_DESDE),
        "fecha_desde_hasta": f"{fecha_str(EDICION_DIAS_HASTA)[:10]} {EDICION_HORA_HASTA}",
    }
    res = acceso_obj.update_full_pass(
        payload_editar_pase(acceso_obj, pase, cambios),
        folio=pase["folio"],
        qr_code=pase_id,
        location=pase["ubicacion"],
    )
    assert res.get("status_code") in (200, 201, 202), f"No se pudo editar el pase: {res}"

    editado = pase_de_la_lista(acceso_obj, pase_id, cambios["nombre"])
    assert editado, f"El pase no aparece en la lista con el nombre nuevo '{cambios['nombre']}'"
    assert editado["empresa"] == cambios["empresa"], f"La empresa quedó '{editado['empresa']}'"
    assert editado["fecha_desde_visita"] == cambios["fecha_desde_visita"], (
        f"La fecha desde quedó '{editado['fecha_desde_visita']}'"
    )
    assert editado["fecha_desde_hasta"] == cambios["fecha_desde_hasta"], (
        f"La fecha hasta quedó '{editado['fecha_desde_hasta']}'"
    )
