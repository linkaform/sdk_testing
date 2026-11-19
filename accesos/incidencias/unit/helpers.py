# coding: utf-8

from ..data.incidencias_data import (
    INCIDENCIA_ANTES,
    GUARDIA_SESION,
    EDITADO_OK,
)


def editar_simulado(acc, mocker, antes=INCIDENCIA_ANTES, editado=EDITADO_OK):
    mocker.patch.object(acc, "_incidencia_formateada", return_value=dict(antes))
    mocker.patch.object(acc, "_reporta_sesion", return_value=GUARDIA_SESION)
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(acc, "get_record_by_folio", return_value={"_id": INCIDENCIA_ANTES["_id"]})
    mocker.patch.object(acc, "agregar_tipo_al_catalogo")
    return {
        "guardar": mocker.patch.object(acc.net, "patch_forms_answers", return_value=dict(editado)),
        "historial": mocker.patch.object(acc, "registrar_cambios_incidencia"),
    }
