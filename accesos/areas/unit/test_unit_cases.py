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
    AREA,
    AREA_RECORD_ID,
    AREAS_DE_UBICACION,
    AREA_SIN_USOS,
    AREA_NUEVA,
    GUARDADO_OK,
    EDICION_PARCIAL,
    ESTADO_INACTIVA,
)

pytestmark = pytest.mark.back("sanic")

C10_TRIGGERS = ["create_new_area", "get_area_by_id", "get_catalog_areas_formatted", "update_area_estado", "update_full_area"]


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


@pytest.mark.unit
@pytest.mark.target("get_area_by_id")
def test_detalle_de_area_sin_record_id_marca_error(accesos_no_api, mocker):
    """
    TB-301: el detalle de un área (pantalla a la que llega el QR físico) se
    pide por record_id; sin él, get_area_by_id debe marcar error sin
    consultar la base.
    """
    acc = accesos_no_api
    cr = mocker.Mock()
    mocker.patch.object(acc, "cr", cr, create=True)

    with pytest.raises(Exception, match="Record ID is required"):
        acc.get_area_by_id("")

    cr.aggregate.assert_not_called()


@pytest.mark.unit
@pytest.mark.target("get_area_by_id")
def test_detalle_de_area_sin_multiple_ubicacion_ni_usos_regresa_no_y_lista_vacia(accesos_no_api, mocker):
    """
    TB-302: un área que no tiene guardados "Múltiple ubicación" ni "Utilizar
    Área en" debe regresar "no" y [] en el detalle, para que el modal de
    edición abra con el switch apagado y sin usos, y no con valores vacíos
    que el front no sabe pintar.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "cr", mocker.Mock(), create=True)
    mocker.patch.object(acc, "format_cr", return_value=dict(AREA_SIN_USOS))

    area = acc.get_area_by_id(AREA_RECORD_ID)

    assert area["multiple_ubicacion"] == "no"
    assert area["usos"] == []
    assert (area["record_id"], area["rondin_area"], area["ubicacion"]) == (AREA_RECORD_ID, AREA, LOCATION)


@pytest.mark.unit
@pytest.mark.target("create_new_area")
def test_area_repetida_en_la_ubicacion_no_se_vuelve_a_crear(accesos_no_api, mocker):
    """
    TB-303: si ya existe un área con ese nombre en la ubicación,
    create_new_area debe responder 208 (la ruta lo muestra como "Área
    duplicada") sin crear otro registro; si no, Disponibles mostraría la
    misma área dos veces.
    """
    acc = accesos_no_api
    existe = mocker.patch.object(acc, "exists_area", return_value=True)
    crear = mocker.patch.object(acc, "create_register")

    respuesta = acc.create_new_area(dict(AREA_NUEVA))

    existe.assert_called_once_with(LOCATION, AREA)
    assert respuesta["status_code"] == 208
    crear.assert_not_called()


@pytest.mark.unit
@pytest.mark.target("create_new_area")
def test_area_nueva_nace_activa_y_disponible(accesos_no_api, mocker):
    """
    TB-304: con los datos de + Nueva Área, create_new_area debe guardar el
    área activa y disponible, con su nombre, su ubicación en el catálogo de
    ubicaciones y su tipo en el catálogo de tipos de área. Si nace inactiva o
    sin ubicación, no aparece en Disponibles.
    """
    acc = accesos_no_api
    mocker.patch.object(acc, "exists_area", return_value=False)
    mocker.patch.object(acc, "get_area_contact_details", return_value={})
    crear = mocker.patch.object(acc, "create_register", return_value=dict(GUARDADO_OK))

    acc.create_new_area(dict(AREA_NUEVA))

    crear.assert_called_once()
    answers = crear.call_args.kwargs["answers"]
    assert answers[acc.f["estatus_config_area"]] == "activa"
    assert answers[acc.f["estatus_area"]] == "disponible"
    assert answers[acc.mf["nombre_area"]] == AREA
    assert answers[acc.Location.UBICACIONES_CAT_OBJ_ID] == {acc.mf["nombre_ubicacion_salida"]: LOCATION}
    assert answers[acc.Location.TIPO_AREA_OBJ_ID] == {acc.f["tipo_de_area"]: AREA_NUEVA["tipo_de_area"]}


@pytest.mark.unit
@pytest.mark.target("update_full_area")
def test_editar_area_solo_cambia_los_campos_enviados(accesos_no_api, mocker):
    """
    TB-305: el modal de edición solo manda los campos que cambian;
    update_full_area debe guardar en el registro del área solo esos campos
    (aquí nombre y tipo). Si manda los demás vacíos, borra la foto, el QR o la
    ubicación que el área ya tenía.
    """
    acc = accesos_no_api
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value=dict(GUARDADO_OK))

    acc.update_full_area(AREA_RECORD_ID, dict(EDICION_PARCIAL))

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["record_id"] == [AREA_RECORD_ID]
    assert guardar.call_args.kwargs["form_id"] == acc.Location.AREAS_DE_LAS_UBICACIONES
    assert guardar.call_args.kwargs["answers"] == {
        acc.mf["nombre_area"]: EDICION_PARCIAL["nombre"],
        acc.Location.TIPO_AREA_OBJ_ID: {acc.f["tipo_de_area"]: EDICION_PARCIAL["tipo_de_area"]},
    }


@pytest.mark.unit
@pytest.mark.target("update_full_area")
def test_editar_area_sin_cambios_no_guarda_nada(accesos_no_api, mocker):
    """
    TB-306: si el modal de edición no manda ningún campo, update_full_area
    debe responder 400 "No hay cambios para guardar." sin llamar al guardado.
    Si guarda, LinkaForm recibe un registro vacío.
    """
    acc = accesos_no_api
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value=dict(GUARDADO_OK))

    res = acc.update_full_area(AREA_RECORD_ID, {})

    guardar.assert_not_called()
    assert res["status_code"] == 400
    assert res["json"]["error"] == "No hay cambios para guardar."


@pytest.mark.unit
@pytest.mark.target("update_area_estado")
def test_desactivar_area_guarda_el_estado_en_esa_area(accesos_no_api, mocker):
    """
    TB-307: al desactivar un área desde Disponibles, update_area_estado debe
    guardar 'inactiva' en el campo de estado de esa área y solo en ella. Si
    lo guarda en otro campo o en otra área, el área sigue activa.
    """
    acc = accesos_no_api
    guardar = mocker.patch.object(acc.lkf_api, "patch_multi_record", return_value=dict(GUARDADO_OK))

    acc.update_area_estado(AREA_RECORD_ID, ESTADO_INACTIVA)

    guardar.assert_called_once()
    assert guardar.call_args.kwargs["record_id"] == [AREA_RECORD_ID]
    assert guardar.call_args.kwargs["form_id"] == acc.Location.AREAS_DE_LAS_UBICACIONES
    assert guardar.call_args.kwargs["answers"] == {acc.Location.f["area_state"]: ESTADO_INACTIVA}
