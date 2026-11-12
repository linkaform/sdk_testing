# coding: utf-8

"""
Contador de vehículos dentro de Bitácoras (get_page_stats, page='Bitacoras')
contra la lista Vehículos → Dentro (get_list_bitacora con desglose='vehiculos').
Notion: TB-099.
"""

import pytest

from .fixtures import *
from ..data.vehiculos_data import (
    LOCATION,
    AREA,
    DESGLOSE_VEHICULOS,
    FILTRO_DENTRO,
    VEHICULOS_CON_Y_SIN_TIPO,
)
from entradas_salidas.integration.helpers import salida_silenciosa


@pytest.mark.integration
@pytest.mark.bug(1484)
def test_contador_de_vehiculos_dentro_cuadra_con_la_lista(acceso_obj, pase_activo):
    """
    TB-099: con una visita abierta que trae un vehículo sin tipo, el contador
    de vehículos dentro de Bitácoras debe marcar lo mismo que el total de la
    lista Vehículos → Dentro, para la misma ubicación y caseta. Si no, la
    tarjeta dice que hay más vehículos dentro de los que el guardia ve en la
    lista (ticket 2610-1484).
    Bug 2610-1484 corregido (addons 7d2eef6).
    """
    res = acceso_obj.do_access(pase_activo, LOCATION, AREA, {"vehiculo": VEHICULOS_CON_Y_SIN_TIPO})
    assert res.get("status_code") in (200, 201, 202), f"No se pudo dar entrada con vehículos: {res}"

    try:
        stats = acceso_obj.get_page_stats(AREA, LOCATION, page="Bitacoras")
        dentro = acceso_obj.get_list_bitacora(
            location=LOCATION, area=AREA, dynamic_filters=FILTRO_DENTRO,
            desglose=DESGLOSE_VEHICULOS, limit=1,
        )

        assert stats["total_vehiculos_dentro"] == dentro["total_records"], (
            f"El contador marca {stats['total_vehiculos_dentro']} vehículos dentro "
            f"y la lista Dentro tiene {dentro['total_records']}"
        )
    finally:
        salida_silenciosa(acceso_obj, pase_activo, LOCATION, AREA)
