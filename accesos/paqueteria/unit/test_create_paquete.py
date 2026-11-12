# coding: utf-8

"""
Recibir un paquete (create_paquete, + Nuevo Paquete) sin tocar preprod: se
simula el guardado y se revisan los answers que se mandan a la forma.
Notion: TB-246 a TB-248.
"""

import copy

import pytest

from ..data.paqueteria_data import LOCATION, AREA, PAQUETE_UNIT, METADATA_PAQUETE, GUARDADO_OK


def guardar_paquete(acceso_obj, mocker, paquete, respuesta=GUARDADO_OK, notificacion=None):
    """Crea el paquete con el guardado simulado; regresa (respuesta, mock del guardado)."""
    mocker.patch.object(acceso_obj.lkf_api, "get_metadata", return_value=dict(METADATA_PAQUETE))
    guardar = mocker.patch.object(acceso_obj.lkf_api, "post_forms_answers", return_value=dict(respuesta))
    res = acceso_obj.create_paquete(copy.deepcopy(paquete), notificacion=notificacion)
    return res, guardar


@pytest.mark.unit
def test_recibir_paquete_guarda_ubicacion_caseta_y_locker_en_sus_catalogos(accesos_no_api, mocker):
    """
    TB-246: create_paquete debe guardar la ubicación en el catálogo de
    ubicaciones, la caseta en el de áreas y el locker en el de lockers. Si
    se pierde uno, el paquete no aparece al filtrar por su caseta o nadie
    sabe en qué locker quedó.
    """
    acc = accesos_no_api

    _, guardar = guardar_paquete(acc, mocker, PAQUETE_UNIT)

    answers = guardar.call_args.args[0]["answers"]
    assert answers[acc.UBICACIONES_CAT_OBJ_ID] == {acc.mf["ubicacion"]: LOCATION}
    assert answers[acc.AREAS_DE_LAS_UBICACIONES_CAT_OBJ_ID] == {acc.mf["nombre_area"]: AREA}
    assert answers[acc.LOCKERS_CAT_OBJ_ID] == {acc.mf["locker_id"]: PAQUETE_UNIT["guardado_en_paqueteria"]}
