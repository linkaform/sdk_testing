# coding: utf-8

"""Áreas: catálogo de áreas (get_catalog_areas_formatted), detalle
(get_area_by_id) y alta (create_new_area), sin tocar la cuenta.
Notion: TB-299 a TB-308.

Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS:
./lkf test corre este archivo cuando cambia alguna funcion de C10_TRIGGERS.
La seccion la sirve Sanic en prod: los tests llevan back("sanic") y en addons
salen SKIPPED.
"""

import pytest

from ..data.areas_data import (
    LOCATION,
    AREAS_DE_UBICACION,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["get_catalog_areas_formatted"]


@pytest.mark.unit
@pytest.mark.target("get_catalog_areas_formatted")
def test_catalogo_de_areas_sin_ubicacion_marca_error(accesos_no_api, mocker):
    """
    TB-299: el catálogo de Áreas se pide por ubicación; si el front no manda
    ninguna (o llega vacía), get_catalog_areas_formatted debe marcar error
    antes de buscar áreas, en lugar de regresar las de todas las ubicaciones.
    """
    acc = accesos_no_api
    buscar = mocker.patch.object(acc, "areas_de_ubicaciones", return_value=[])

    with pytest.raises(Exception, match="Ubicacion is required"):
        acc.get_catalog_areas_formatted(locations=[""])

    buscar.assert_not_called()


@pytest.mark.unit
@pytest.mark.target("get_catalog_areas_formatted")
def test_catalogo_de_areas_trae_primero_las_mas_recientes_y_pagina(accesos_no_api, mocker):
    """
    TB-300: en Disponibles las áreas más recientes (folio más alto) salen
    primero y la paginación cuadra: con 3 áreas y 2 por página, la página 1
    trae las 2 más nuevas, la 2 trae la restante, y ambas dicen 3 en total y
    2 páginas.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "areas_de_ubicaciones", return_value=["Caseta Principal", "Almacén", "Estacionamiento"])
    mocker.patch.object(acc, "get_areas_details", return_value=[dict(a) for a in AREAS_DE_UBICACION])

    pagina_1 = acc.get_catalog_areas_formatted(locations=[LOCATION], limit=2, skip=0)
    pagina_2 = acc.get_catalog_areas_formatted(locations=[LOCATION], limit=2, skip=2)

    assert [r["folio"] for r in pagina_1["records"]] == ["12-10", "10-10"]
    assert [r["folio"] for r in pagina_2["records"]] == ["9-10"]
    assert (pagina_1["total_records"], pagina_1["total_pages"]) == (3, 2)
    assert (pagina_1["actual_page"], pagina_1["records_on_page"]) == (1, 2)
    assert (pagina_2["actual_page"], pagina_2["records_on_page"]) == (2, 1)
