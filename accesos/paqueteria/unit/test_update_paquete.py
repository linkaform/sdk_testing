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
