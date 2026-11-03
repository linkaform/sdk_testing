# coding: utf-8

"""
Contador de equipos dentro de Bitácoras (get_page_stats, page='Bitacoras')
contra la lista Equipos → Dentro (get_list_bitacora con desglose='equipos').
Notion: TB-106.
"""

import pytest

from .fixtures import *
from ..data.equipos_data import (
    LOCATION,
    AREA,
    DESGLOSE_EQUIPOS,
    FILTRO_DENTRO,
    EQUIPO_CONTADOR,
)
from entradas_salidas.integration.helpers import salida_silenciosa


@pytest.mark.integration
def test_contador_de_equipos_dentro_cuadra_con_la_lista(acceso_obj, pase_activo):
    """
    TB-106: con una visita abierta con equipo, el contador de equipos dentro
    de Bitácoras debe marcar lo mismo que el total de la lista Equipos →
    Dentro, para la misma ubicación y caseta. Si no, la tarjeta y la lista
    no coinciden y el guardia no sabe cuántos equipos siguen dentro.
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"equipo": [EQUIPO_CONTADOR]})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con equipo: {res}"

    try:
        stats = acceso_obj.get_page_stats(AREA, LOCATION, page="Bitacoras")
        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO,
            desglose=DESGLOSE_EQUIPOS, limit=1,
        )

        assert stats["total_equipos_dentro"] == dentro["total_records"], (
            f"El contador marca {stats['total_equipos_dentro']} equipos dentro "
            f"y la lista Dentro tiene {dentro['total_records']}"
        )
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)
