# coding: utf-8

"""
Catálogo de áreas (Disponibles y modal de recorridos;
get_catalog_areas_formatted en Sanic) sin tocar la cuenta: se simula la
consulta y se revisa qué se pide y qué regresa.
Notion: TB-343 y TB-344.
"""

import pytest

from ..data.catalogo_areas_data import (
    LOCATION,
    AREA,
    AREAS_HOMONIMAS,
)

pytestmark = pytest.mark.back("sanic")


def test_disponibles_no_trae_areas_homonimas_de_otra_ubicacion(accesos_no_api, mocker):
    """
    TB-343: Disponibles de una ubicación debe traer solo sus áreas. Si otra
    ubicación tiene un área con el mismo nombre, no debe aparecer. Hoy la
    consulta filtra solo por nombre de área, así que el área homónima de la
    otra ubicación sale en la lista y cuenta en el total y la paginación.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "areas_de_ubicaciones", return_value=[AREA])
    cr = mocker.MagicMock()
    cr.aggregate.return_value = [dict(a) for a in AREAS_HOMONIMAS]
    mocker.patch.object(acc, "cr", cr, create=True)

    res = acc.get_catalog_areas_formatted(locations=[LOCATION])

    ubicaciones = {r["ubicacion"] for r in res["records"]}
    assert ubicaciones == {LOCATION}, f"Disponibles de {LOCATION} trae áreas de: {ubicaciones}"
    assert res["total_records"] == 1, f"El total cuenta {res['total_records']} áreas"
