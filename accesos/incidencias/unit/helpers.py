# coding: utf-8

from ..data.incidencias_data import (
    INCIDENCIA_ANTES,
    INCIDENCIA_CON_FALLA,
    FALLA_GENERADA_ID,
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


def incidencia_con_falla(acc):
    """Incidencia de antes con la liga a su falla, armada como la guarda el back."""
    return {**INCIDENCIA_CON_FALLA, "falla_generada_url": acc._url_registro_lkf(FALLA_GENERADA_ID)}


def seguimiento_simulado(acc, mocker, encontradas):
    """Simula la incidencia que busca update_incidence_seguimiento (encontradas:
    lo que regresa get_list_incidences) y el guardado; regresa el mock del guardado."""
    mocker.patch.object(acc, "get_list_incidences", return_value=encontradas)
    mocker.patch.object(acc, "_reporta_sesion", return_value=GUARDIA_SESION)
    mocker.patch.object(acc.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(acc, "get_record_by_folio", return_value={"_id": INCIDENCIA_ANTES["_id"]})
    mocker.patch.object(acc, "registrar_cambios_incidencia")
    return mocker.patch.object(acc.net, "patch_forms_answers", return_value=dict(EDITADO_OK))
