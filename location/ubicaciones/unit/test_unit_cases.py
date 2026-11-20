# coding: utf-8

"""Ubicaciones: crear una ubicación (create_new_ubicacion) y su contacto del
catálogo, sin tocar la cuenta.
Notion: TB-351 a TB-360.

Unitarios principales de la seccion (maximo 10) y sus C10_TRIGGERS:
./lkf test corre este archivo cuando cambia alguna funcion de C10_TRIGGERS.
La seccion la sirve Sanic en prod: los tests llevan back("sanic") y en addons
salen SKIPPED.
"""

import pytest

from ..data.ubicaciones_data import (
    NOMBRE_VACIO,
    UBICACION_QA,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["create_new_ubicacion"]


@pytest.mark.unit
@pytest.mark.target("create_new_ubicacion")
def test_crear_una_ubicacion_sin_nombre_da_error_y_no_guarda(location_no_api, mocker):
    """
    TB-351: el nombre es lo que identifica a la ubicación en todos los
    catálogos (casetas, áreas, pases). Sin nombre, o solo con espacios,
    create_new_ubicacion debe responder error sin mandar nada a guardar.
    """
    loc = location_no_api
    guardar = mocker.patch.object(loc.lkf_api, "post_forms_answers")

    with pytest.raises(Exception, match="nombre de la ubicaci.*es requerido"):
        loc.create_new_ubicacion(nombre=NOMBRE_VACIO)

    guardar.assert_not_called()


@pytest.mark.unit
@pytest.mark.target("create_new_ubicacion")
def test_crear_una_ubicacion_con_un_nombre_que_ya_existe_da_error_y_no_guarda(location_no_api, mocker):
    """
    TB-352: dos ubicaciones con el mismo nombre no se distinguen en los
    catálogos que las usan. Si el nombre ya existe, create_new_ubicacion debe
    responder "Ubicación duplicada" sin mandar nada a guardar.
    """
    loc = location_no_api
    mocker.patch.object(loc, "exists_ubicacion", return_value=True)
    guardar = mocker.patch.object(loc.lkf_api, "post_forms_answers")

    with pytest.raises(Exception, match="Ya existe una ubicaci"):
        loc.create_new_ubicacion(nombre=UBICACION_QA)

    guardar.assert_not_called()
