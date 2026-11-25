# coding: utf-8

"""
Conteos del buscador de Disponibles (get_search_counts_areas en Sanic) sin
tocar la cuenta: se simula la consulta y se revisa qué se pide.
Notion: TB-381.
"""

import pytest

from ..data.areas_data import (
    LOCATION,
    AREA,
    CANDIDATOS_BUSCADOR,
)

pytestmark = pytest.mark.back("sanic")


@pytest.mark.bug(1605)
def test_conteos_del_buscador_no_cuentan_areas_homonimas_de_otra_ubicacion(accesos_no_api, mocker):
    """
    TB-381: los chips del buscador cuentan las áreas de las ubicaciones
    elegidas. La consulta se arma con los nombres de esas áreas; si no filtra
    también por la ubicación, un área con el mismo nombre en otra ubicación
    suma en los conteos (lo mismo que TB-343 en la lista).
    Ticket 2611-1605.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "areas_de_ubicaciones", return_value=[AREA])
    cr = mocker.MagicMock()
    cr.aggregate.return_value = []
    mocker.patch.object(acc, "cr", cr, create=True)

    acc.get_search_counts_areas(locations=[LOCATION], candidates=[dict(c) for c in CANDIDATOS_BUSCADOR])

    consulta = cr.aggregate.call_args.args[0]
    assert LOCATION in str(consulta), f"La consulta de los conteos no filtra por {LOCATION}: {consulta}"
