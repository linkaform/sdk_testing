# coding: utf-8

"""
Pestaña Incidencias del detalle de un área (get_incidencias_by_area en
Sanic) sin tocar la cuenta: se simulan el área y los rondines y se revisa qué
regresa.
Notion: TB-384 y TB-385.
"""

import pytest

from ..data.areas_data import (
    AREA_RECORD_ID,
)

pytestmark = pytest.mark.back("sanic")


@pytest.mark.unit
@pytest.mark.target("get_incidencias_by_area")
def test_pestana_incidencias_de_un_area_que_no_existe_regresa_una_pagina_vacia(accesos_no_api, mocker):
    """
    TB-384: el detalle de un área se abre por su record_id (el QR físico
    apunta a él). Si el área ya no existe, get_area_by_id regresa None y la
    pestaña Incidencias debe mostrar una página vacía, no tronar. Lo mismo
    hace get_rondines_by_area para la pestaña Rondines.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "get_area_by_id", return_value=None)
    cr = mocker.MagicMock()
    cr.aggregate.return_value = []
    mocker.patch.object(acc, "cr", cr, create=True)

    res = acc.get_incidencias_by_area(AREA_RECORD_ID, limit=0)

    assert res["records"] == []
    assert res["total_records"] == 0
