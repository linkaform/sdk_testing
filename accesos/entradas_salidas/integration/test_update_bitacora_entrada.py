# coding: utf-8

"""
Editar una entrada de la bitácora (update_bitacora_entrada): agregar o editar
vehículos y equipos de una visita.
Notion: TB-064 a TB-067.
"""

import pytest

from .fixtures import *
from ..data.bitacora_data import VEHICULO_PRUEBA
from .helpers import ultima_visita


@pytest.mark.integration
def test_update_bitacora_entrada_agrega_vehiculo(acceso_obj, pase_dentro):
    """
    TB-064: con action='create', update_bitacora_entrada agrega un vehículo a
    la visita abierta sin tocar los que ya tenía. Es lo que usa el guardia
    cuando la persona llega en un vehículo que no estaba en el pase.
    """
    folio, entrada = pase_dentro
    antes = ultima_visita(acceso_obj, folio).get("vehiculos") or []

    acceso_obj.update_bitacora_entrada(
        {"action": "create", "vehiculo": VEHICULO_PRUEBA}, record_id=entrada["_id"]
    )

    despues = ultima_visita(acceso_obj, folio).get("vehiculos") or []
    assert len(despues) == len(antes) + 1, f"Se esperaba 1 vehículo más: antes={len(antes)}, después={len(despues)}"
    assert VEHICULO_PRUEBA["placas"] in {v.get("placas") for v in despues}, (
        f"El vehículo agregado no aparece en la visita: {despues}"
    )
