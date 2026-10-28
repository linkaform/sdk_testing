# coding: utf-8

"""
Gafete y locker de una entrada (assing_gafete) en la bitácora de Entradas & Salidas.
Notion: TB-067.

assing_gafete guarda gafete, locker y documento en el registro de la visita y,
con tipo_movimiento='entrada', marca el gafete y el locker de identificaciones
como 'En Uso' en sus catálogos.
"""

import pytest

from .fixtures import *
from ..data.bitacora_data import LOCATION, AREA, DOCUMENTO_GAFETE
from .helpers import gafete_y_locker_disponibles, ultima_visita


@pytest.mark.integration
def test_assing_gafete_entrada_guarda_y_marca_en_uso(acceso_obj, pase_dentro):
    """
    TB-067: al asignar gafete y locker a una entrada, la visita debe guardarlos
    y los dos deben quedar 'En Uso'. Si no, otro guardia podría entregar el
    mismo gafete o locker a otra persona.
    """
    folio, entrada = pase_dentro
    gafete_id, locker_id = gafete_y_locker_disponibles(acceso_obj, LOCATION, AREA)
    if not gafete_id:
        pytest.skip(f"No hay gafete y locker 'Disponible' en {LOCATION} / {AREA} en esta cuenta")

    datos_gafete = {
        "gafete_id": gafete_id,
        "locker_id": locker_id,
        "ubicacion": LOCATION,
        "area": AREA,
        "documento": DOCUMENTO_GAFETE,
    }
    asignado = acceso_obj.assing_gafete(
        {**datos_gafete, "status_gafete": "asignado"}, entrada["_id"], "entrada"
    )

    try:
        assert asignado, "assing_gafete no regresó respuesta al asignar"

        visita = ultima_visita(acceso_obj, folio)
        assert visita["_id"] == entrada["_id"], "assing_gafete modificó otro registro"
        assert visita["gafete_id"] == gafete_id, f"La visita no guardó el gafete: {visita['gafete_id']}"
        assert visita["locker_id"] == locker_id, f"La visita no guardó el locker: {visita['locker_id']}"

        gafetes = acceso_obj.get_gafetes(status=None, location=LOCATION, area=AREA, gafete_id=gafete_id)
        assert gafetes, f"El gafete {gafete_id} no aparece en el catálogo"
        assert gafetes[0]["status"] == "En Uso", f"El gafete quedó '{gafetes[0]['status']}'"

        lockers = acceso_obj.get_lockers(
            status=None, location=LOCATION, area=AREA, tipo_locker="Identificaciones", locker_id=locker_id
        )
        assert lockers, f"El locker {locker_id} no aparece en el catálogo"
        assert lockers[0]["status"] == "En Uso", f"El locker quedó '{lockers[0]['status']}'"
    finally:
        # Devuelve el gafete para no dejarlo 'En Uso' en preprod y permitir la salida.
        acceso_obj.assing_gafete(
            {**datos_gafete, "documento": "", "status_gafete": "entregado"}, entrada["_id"], "salida"
        )
