# coding: utf-8

"""
Lista de la bitácora (list_bitacora2 → get_list_bitacora): rango de fechas y
filtro por ubicación.
Notion: TB-048 a TB-050.
"""

import pytest

from .fixtures import *
from ..data.bitacora_data import LOCATION, AREA


@pytest.mark.integration
def test_list_bitacora_rango_de_fechas_solo_aplica_con_filterdate_range(acceso_obj):
    """
    TB-048: el front manda filterDate='range' cuando el usuario elige fechas a
    mano. Con 'range' el filtro va sobre fecha_entrada y un dateTo de solo día
    se extiende al final de ese día; sin 'range', dateFrom/dateTo se ignoran.
    """
    campo_entrada = f"answers.{acceso_obj.mf['fecha_entrada']}"
    desde, hasta = "2026-01-01", "2026-01-31"

    con_range = acceso_obj.bitacora_base_match(
        location=LOCATION, area=AREA, dateFrom=desde, dateTo=hasta, filterDate="range",
    )
    assert con_range.get(campo_entrada) == {"$gte": desde, "$lte": f"{hasta} 23:59:59"}, (
        f"Filtro de rango inesperado: {con_range.get(campo_entrada)}"
    )

    sin_range = acceso_obj.bitacora_base_match(
        location=LOCATION, area=AREA, dateFrom=desde, dateTo=hasta, filterDate="",
    )
    assert campo_entrada not in sin_range, (
        f"Sin filterDate='range' no debería filtrar por fecha: {sin_range.get(campo_entrada)}"
    )
