# coding: utf-8

"""
Agregar un equipo a una visita abierta desde el modal de agregar equipo
(add-local-equipo.tsx → update_bitacora_entrada sin action) y verlo en
Equipos → Dentro.
Notion: TB-104 y TB-105.
"""

import pytest

from .fixtures import *
from ..data.equipos_data import (
    LOCATION,
    AREA,
    LIMITE_LISTA,
    DESGLOSE_EQUIPOS,
    FILTRO_DENTRO,
    EQUIPO_AGREGADO,
)
from entradas_salidas.integration.helpers import dar_entrada, salida_silenciosa


@pytest.mark.integration
def test_agregar_equipo_a_visita_abierta_aparece_en_dentro(acceso_obj, pase_activo):
    """
    TB-104: a una visita abierta sin equipo, el guardia le agrega uno desde
    el modal de agregar equipo (update_bitacora_entrada sin action). Debe
    aparecer como fila en Equipos → Dentro con su número de serie; si no, el
    equipo queda dentro sin que nadie lo vea en la lista.
    """
    visita = dar_entrada(acceso_obj, pase_activo, LOCATION, AREA)

    try:
        acceso_obj.update_bitacora_entrada({"equipo": EQUIPO_AGREGADO}, record_id=visita["_id"])

        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO,
            desglose=DESGLOSE_EQUIPOS, limit=LIMITE_LISTA,
        )
        filas_visita = [r for r in dentro["records"] if r["_id"] == visita["_id"]]
        assert len(filas_visita) == 1, f"El equipo agregado no aparece en Dentro: {len(filas_visita)} filas"
        assert filas_visita[0]["equipos"][0]["numero_serie"] == EQUIPO_AGREGADO["serie"]
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)
