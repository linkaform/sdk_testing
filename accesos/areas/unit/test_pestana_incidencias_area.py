# coding: utf-8

"""
Pestaña Incidencias del detalle de un área (get_incidencias_by_area en
Sanic) sin tocar la cuenta: se simulan el área y los rondines y se revisa qué
regresa.
Notion: TB-385.
"""

import copy

import pytest

from ..data.areas_data import (
    AREA,
    AREA_RECORD_ID,
    AREA_DETALLE,
    RONDINES_CON_INCIDENCIAS,
    LIMIT_TODAS,
)

pytestmark = pytest.mark.back("sanic")


@pytest.mark.unit
@pytest.mark.target("get_incidencias_by_area")
def test_pestana_incidencias_del_area_con_limit_0_regresa_todas_en_una_pagina(accesos_no_api, mocker):
    """
    TB-385: el front pide la pestaña Incidencias con limit 0 para traer
    todas. Deben salir las 3 incidencias de esta área en una sola página, sin
    la de otra área revisada en el mismo rondín.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "get_area_by_id", return_value=dict(AREA_DETALLE))
    mocker.patch.object(acc, "cr", mocker.MagicMock(), create=True)
    mocker.patch.object(acc, "format_cr", return_value=copy.deepcopy(RONDINES_CON_INCIDENCIAS))

    res = acc.get_incidencias_by_area(AREA_RECORD_ID, limit=LIMIT_TODAS)

    assert {r["area_incidente"] for r in res["records"]} == {AREA}
    assert (res["total_records"], res["records_on_page"]) == (3, 3)
    assert (res["total_pages"], res["actual_page"]) == (1, 1)
