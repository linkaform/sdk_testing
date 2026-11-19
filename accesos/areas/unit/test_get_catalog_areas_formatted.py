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


@pytest.mark.bug(1605)
def test_disponibles_no_trae_areas_homonimas_de_otra_ubicacion(accesos_no_api, mocker):
    """
    TB-343: Disponibles de una ubicación debe traer solo sus áreas. Si otra
    ubicación tiene un área con el mismo nombre, no debe aparecer. Hoy la
    consulta filtra solo por nombre de área, así que el área homónima de la
    otra ubicación sale en la lista y cuenta en el total y la paginación.
    Ticket 2611-1605.
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


def test_catalogo_de_areas_trae_los_usos_para_priorizar_las_de_rondines(accesos_no_api, mocker):
    """
    TB-344: get_catalog_areas_formatted pone primero las áreas marcadas para
    "rondines" (campo Utilizar Área en), pero la consulta de get_areas_details
    no trae ese campo, así que el filtro nunca se aplica y el modal de
    recorridos recibe todas las áreas. La consulta debe traer los usos.
    """
    acc = accesos_no_api
    cr = mocker.MagicMock()
    cr.aggregate.return_value = []
    mocker.patch.object(acc, "cr", cr, create=True)

    acc.get_areas_details([AREA])

    consulta = cr.aggregate.call_args.args[0]
    proyeccion = next(paso["$project"] for paso in consulta if "$project" in paso)
    assert "usos" in proyeccion, f"La consulta no trae los usos: {sorted(proyeccion)}"
