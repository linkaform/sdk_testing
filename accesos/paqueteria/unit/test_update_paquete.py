# coding: utf-8

"""
Editar un paquete (update_paquete: editar-paqueteria) sin tocar preprod: se
simula el guardado y se revisa que cada campo se guarde donde lo guarda
create_paquete.
Notion: TB-251 a TB-253.
"""

import pytest

from ..data.paqueteria_data import (
    LOCATION,
    AREA,
    FOLIO_PAQUETE,
    EDICION_OK,
    EDICION_PAQUETE,
)


def answers_editados(acceso_obj, mocker):
    """Edita el paquete con el guardado simulado y regresa los answers que se mandaron."""
    guardar = mocker.patch.object(acceso_obj.lkf_api, "patch_multi_record", return_value=dict(EDICION_OK))
    acceso_obj.update_paquete(dict(EDICION_PAQUETE), FOLIO_PAQUETE)
    guardar.assert_called_once()
    return guardar.call_args.kwargs["answers"]


def test_editar_caseta_del_paquete_la_guarda_donde_la_guarda_la_creacion(accesos_no_api, mocker):
    """
    TB-251: al editar un paquete, update_paquete debe guardar la caseta en el
    catálogo de áreas con el campo nombre_area, igual que create_paquete. Si
    la guarda en otro campo, el paquete editado deja de salir al filtrar por
    su caseta.
    """
    acc = accesos_no_api

    answers = answers_editados(acc, mocker)

    caseta = answers.get(acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID)
    assert caseta == {acc.mf["nombre_area"]: AREA}, f"La caseta quedó {caseta!r}"


def test_editar_destinatario_empleado_lo_guarda_en_el_catalogo_de_empleados(accesos_no_api, mocker):
    """
    TB-252: al editar un paquete con destinatario empleado, update_paquete
    debe guardarlo en el catálogo de empleados, igual que create_paquete. Si
    lo guarda suelto, el paquete pierde a su destinatario.
    """
    acc = accesos_no_api

    answers = answers_editados(acc, mocker)

    destinatario = answers.get(acc.CONF_AREA_EMPLEADOS_CAT_OBJ_ID)
    esperado = {acc.mf["nombre_empleado"]: EDICION_PAQUETE["quien_recibe_paqueteria"]}
    assert destinatario == esperado, f"El destinatario quedó {destinatario!r} en el catálogo de empleados"


def test_editar_ubicacion_del_paquete_la_guarda_en_el_catalogo_de_ubicaciones(accesos_no_api, mocker):
    """
    TB-253: al editar un paquete, update_paquete debe guardar la ubicación en
    el catálogo de ubicaciones, igual que create_paquete. Si la guarda con
    otra llave, el paquete editado deja de salir al filtrar por su ubicación.
    """
    acc = accesos_no_api

    answers = answers_editados(acc, mocker)

    ubicacion = answers.get(acc.UBICACIONES_CAT_OBJ_ID)
    assert ubicacion == {acc.mf["ubicacion"]: LOCATION}, f"La ubicación quedó {ubicacion!r}"
