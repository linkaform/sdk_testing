# coding: utf-8

"""Ubicaciones: crear una ubicación (create_new_ubicacion) y su contacto del
catálogo y editarla (update_ubicacion), sin tocar la cuenta.
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
    DIRECCION_UBICACION,
    CREADO_OK,
    CONTACTO_QA,
    DIRECCION_CONTACTO,
    CIUDAD_CONTACTO,
    ID_CONTACTO,
    REGISTRO_UBICACION,
    UBICACION_GUARDADA,
    UBICACION_RENOMBRADA,
    EDITADO_OK,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["_contacto_answers", "_contacto_ubicacion_desde_catalogo", "_get_contacto_catalogo", "create_contacto", "create_new_ubicacion", "update_ubicacion"]


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


@pytest.mark.unit
@pytest.mark.target("create_new_ubicacion", "_contacto_answers")
def test_una_ubicacion_sin_contacto_elegido_da_de_alta_su_contacto_con_la_direccion(location_no_api, mocker):
    """
    TB-353: si no se elige un contacto del catálogo, create_new_ubicacion da
    de alta uno con el nombre de la ubicación y la dirección capturada, y la
    ubicación apunta a él: el nombre va suelto y los demás campos como lista,
    igual que los registros existentes. Si no, LinkaForm rechaza el contacto
    o la ubicación queda sin dirección.
    """
    loc = location_no_api
    f = loc.f
    mocker.patch.object(loc, "exists_ubicacion", return_value=False)
    mocker.patch.object(loc.lkf_api, "search_catalog", return_value=[])
    mocker.patch.object(loc.lkf_api, "get_catalog_metadata", return_value={})
    alta_contacto = mocker.patch.object(loc.lkf_api, "post_catalog_answers", return_value=dict(CREADO_OK))
    mocker.patch.object(loc.lkf_api, "get_metadata", return_value={})
    guardar = mocker.patch.object(loc.lkf_api, "post_forms_answers", return_value=dict(CREADO_OK))

    loc.create_new_ubicacion(nombre=UBICACION_QA, **DIRECCION_UBICACION)

    contacto = alta_contacto.call_args.args[0]["answers"]
    assert contacto[f["address_name"]] == UBICACION_QA
    assert contacto[f["address"]] == DIRECCION_UBICACION["direccion"]
    answers = guardar.call_args.args[0]["answers"]
    assert answers[f["location"]] == UBICACION_QA
    ubicacion_contacto = answers[loc.CONTACTO_CAT_OBJ_ID]
    assert ubicacion_contacto[f["address_name"]] == UBICACION_QA
    assert ubicacion_contacto[f["address"]] == [DIRECCION_UBICACION["direccion"]]
    assert ubicacion_contacto[f["city"]] == [DIRECCION_UBICACION["ciudad"]]


@pytest.mark.unit
@pytest.mark.target("create_new_ubicacion", "_contacto_ubicacion_desde_catalogo")
def test_una_ubicacion_con_contacto_del_catalogo_apunta_a_el_sin_crear_otro(location_no_api, mocker):
    """
    TB-354: si se elige un contacto que ya existe en el catálogo,
    create_new_ubicacion apunta la ubicación a ese contacto y no da de alta
    otro. Del registro del catálogo no se copian su _id ni su estatus: la
    ubicación solo lleva los datos de la dirección.
    """
    loc = location_no_api
    f = loc.f
    registro = {
        "_id": ID_CONTACTO,
        f["address_name"]: CONTACTO_QA,
        f["address"]: DIRECCION_CONTACTO,
        f["city"]: CIUDAD_CONTACTO,
        loc.CONTACTO_STATUS_FIELD: "Activo",
    }
    mocker.patch.object(loc, "exists_ubicacion", return_value=False)
    mocker.patch.object(loc.lkf_api, "search_catalog", return_value=[registro])
    alta_contacto = mocker.patch.object(loc.lkf_api, "post_catalog_answers")
    mocker.patch.object(loc.lkf_api, "get_metadata", return_value={})
    guardar = mocker.patch.object(loc.lkf_api, "post_forms_answers", return_value=dict(CREADO_OK))

    loc.create_new_ubicacion(nombre=UBICACION_QA, contacto=CONTACTO_QA)

    alta_contacto.assert_not_called()
    answers = guardar.call_args.args[0]["answers"]
    assert answers[loc.CONTACTO_CAT_OBJ_ID] == {
        f["address_name"]: CONTACTO_QA,
        f["address"]: [DIRECCION_CONTACTO],
        f["city"]: [CIUDAD_CONTACTO],
    }


@pytest.mark.unit
@pytest.mark.target("create_new_ubicacion", "_get_contacto_catalogo")
def test_un_contacto_que_no_existe_en_el_catalogo_da_error_y_no_guarda_la_ubicacion(location_no_api, mocker):
    """
    TB-355: LinkaForm solo acepta en el campo de contacto valores que existen
    en el catálogo. Si el contacto elegido ya no está, create_new_ubicacion
    debe responder "Contacto no encontrado" sin guardar la ubicación.
    """
    loc = location_no_api
    mocker.patch.object(loc, "exists_ubicacion", return_value=False)
    mocker.patch.object(loc.lkf_api, "search_catalog", return_value=[])
    guardar = mocker.patch.object(loc.lkf_api, "post_forms_answers")

    with pytest.raises(Exception, match="No existe el contacto"):
        loc.create_new_ubicacion(nombre=UBICACION_QA, contacto=CONTACTO_QA)

    guardar.assert_not_called()


@pytest.mark.unit
@pytest.mark.target("update_ubicacion")
def test_editar_una_ubicacion_sin_cambios_no_guarda_nada(location_no_api, mocker):
    """
    TB-356: si la ubicación se guarda con el mismo nombre y el mismo
    contacto, update_ubicacion responde "Sin cambios" sin mandar nada a
    guardar. Un guardado vacío solo crea una versión nueva del registro.
    """
    loc = location_no_api
    mocker.patch.object(loc, "get_ubicacion_by_id", return_value=dict(UBICACION_GUARDADA))
    guardar = mocker.patch.object(loc.lkf_api, "patch_multi_record")

    res = loc.update_ubicacion(record_id=REGISTRO_UBICACION, nombre=UBICACION_QA, contacto=CONTACTO_QA)

    guardar.assert_not_called()
    assert res["status_code"] == 200


@pytest.mark.unit
@pytest.mark.target("update_ubicacion")
def test_cambiar_el_nombre_de_una_ubicacion_solo_manda_el_nombre(location_no_api, mocker):
    """
    TB-357: al renombrar una ubicación sin cambiar su contacto,
    update_ubicacion manda a guardar solo el campo del nombre en ese registro.
    Si mandara el contacto también, LinkaForm lo volvería a validar contra el
    catálogo sin necesidad.
    """
    loc = location_no_api
    mocker.patch.object(loc, "get_ubicacion_by_id", return_value=dict(UBICACION_GUARDADA))
    guardar = mocker.patch.object(loc.lkf_api, "patch_multi_record", return_value=dict(EDITADO_OK))

    loc.update_ubicacion(record_id=REGISTRO_UBICACION, nombre=UBICACION_RENOMBRADA, contacto=CONTACTO_QA)

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["answers"] == {loc.f["location"]: UBICACION_RENOMBRADA}
    assert guardar.call_args.kwargs["record_id"] == [REGISTRO_UBICACION]


@pytest.mark.unit
@pytest.mark.target("create_contacto", "_get_contacto_catalogo")
def test_dar_de_alta_un_contacto_con_un_nombre_que_ya_existe_da_error(location_no_api, mocker):
    """
    TB-358: el botón "+" del selector de dirección da de alta un contacto en
    el catálogo. Si ya hay uno con ese nombre, create_contacto debe responder
    "Contacto duplicado" sin darlo de alta: dos contactos con el mismo nombre
    no se distinguen en el selector.
    """
    loc = location_no_api
    registro = {loc.f["address_name"]: CONTACTO_QA, loc.f["address"]: DIRECCION_CONTACTO}
    mocker.patch.object(loc.lkf_api, "search_catalog", return_value=[registro])
    alta_contacto = mocker.patch.object(loc.lkf_api, "post_catalog_answers")

    with pytest.raises(Exception, match="Ya existe un contacto"):
        loc.create_contacto(nombre=CONTACTO_QA, direccion=DIRECCION_CONTACTO)

    alta_contacto.assert_not_called()
