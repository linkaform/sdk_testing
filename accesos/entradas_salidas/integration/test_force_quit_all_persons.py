# coding: utf-8

"""
Salida masiva por ubicación (force_quit_all_persons) en la bitácora de
Entradas & Salidas. Cierra TODAS las visitas abiertas de LOCATION en
preprod, no solo las del test (autorizado para Planta Monterrey).
Notion: TB-070.
"""

import pytest

from .fixtures import *
from ..data.bitacora_data import LOCATION
from .helpers import ultima_visita


@pytest.mark.integration
def test_force_quit_por_ubicacion_cierra_solo_esa_ubicacion(acceso_obj, pase_dentro, pase_dentro_otra_ubicacion):
    """
    TB-070: la salida masiva de LOCATION pasa a salida las visitas abiertas
    de esa ubicación y deja abiertas las de otras ubicaciones de la cuenta.
    """
    folio, _ = pase_dentro
    folio_otra, _ = pase_dentro_otra_ubicacion

    res = acceso_obj.force_quit_all_persons(location=LOCATION)
    assert res.get("status_code") in (200, 201, 202), f"La salida masiva no se ejecutó: {res}"

    visita = ultima_visita(acceso_obj, folio)
    assert visita["status_visita"] == "salida", f"La visita de {LOCATION} sigue en '{visita['status_visita']}'"

    visita_otra = ultima_visita(acceso_obj, folio_otra)
    assert visita_otra["status_visita"] == "entrada", (
        f"La salida masiva de {LOCATION} cerró una visita de {visita_otra.get('ubicacion_entrada')}"
    )

