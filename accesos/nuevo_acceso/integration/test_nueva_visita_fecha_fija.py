# coding: utf-8

"""
Pase creado desde el modal "Nueva Visita" (+ Nuevo Acceso) en modo Fecha Fija,
con el payload que arma el front (add-visit-modal.tsx + lib/access.ts).
Notion: TB-160.
"""

import pytest

from .fixtures import *


@pytest.mark.integration
@pytest.mark.bug(1547)
def test_nueva_visita_fecha_fija_hoy_crea_el_pase(acceso_obj, mock_pase_fecha_fija_hoy):
    """
    TB-160: al guardar Nueva Visita en Fecha Fija con la fecha de hoy, el
    front manda fecha_desde_visita = ayer (el día anterior a la fecha
    elegida). create_access_pass debe crear el pase (201); si lo rechaza por
    "fecha de visita en el pasado", el guardia no puede registrar una visita
    de Fecha Fija para el mismo día.
    """
    try:
        res = acceso_obj.create_access_pass(mock_pase_fecha_fija_hoy)
    except Exception as e:
        pytest.fail(f"create_access_pass rechazó el pase de Fecha Fija para hoy: {e}")

    assert res.get("status_code") == 201, f"No se pudo crear el pase de Fecha Fija para hoy: {res}"
