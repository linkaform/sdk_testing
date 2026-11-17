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
