# coding: utf-8

from ..data.incidencias_data import (
    INCIDENCIA_CON_FALLA,
    GUARDIA_SESION,
    EDITADO_OK,
)


def edicion_simulada(acceso_obj, mocker, antes=INCIDENCIA_CON_FALLA):
    """
    Simula lo que update_incidence y update_incidence_seguimiento consultan
    fuera (la incidencia de antes, la sesión, la forma) y regresa el mock del
    guardado, para revisar los answers que se mandan.
    """
    mocker.patch.object(acceso_obj, "_incidencia_formateada", return_value=dict(antes))
    mocker.patch.object(acceso_obj, "get_list_incidences", return_value=[dict(antes)])
    mocker.patch.object(acceso_obj, "_reporta_sesion", return_value=GUARDIA_SESION)
    mocker.patch.object(acceso_obj.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(acceso_obj, "get_record_by_folio", return_value={"_id": antes["_id"]})
    mocker.patch.object(acceso_obj, "agregar_tipo_al_catalogo")
    mocker.patch.object(acceso_obj, "registrar_cambios_incidencia")
    return mocker.patch.object(acceso_obj.net, "patch_forms_answers", return_value=dict(EDITADO_OK))
