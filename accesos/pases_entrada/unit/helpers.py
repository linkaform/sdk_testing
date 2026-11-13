# coding: utf-8

import copy
from datetime import timedelta

from lkf_back import de

from ..data.pases_entrada_data import (
    NOMBRE_PASE_UNIT,
    FOTO_VALIDA,
    IDENTIFICACION_VALIDA,
    ANFITRION_PASE,
    AUTORIZADO_POR,
    PASE_NUEVO,
    DIAS_VIGENTE,
    PASE_GUARDADO,
)


def fecha_hasta(acceso_obj, dias):
    """Fecha "hasta" del pase a `dias` de hoy, con el mismo hoy que usa access_pass_set_status."""
    return (acceso_obj.get_today_format() + timedelta(days=dias)).strftime("%Y-%m-%d 23:59:59")


def answers_pase(acceso_obj, **campos):
    """Answers del pase con los ids de pase_entrada_fields; sin anfitrión en grupo_visitados."""
    answers = {acceso_obj.pase_entrada_fields["grupo_visitados"]: []}
    for campo, valor in campos.items():
        answers[acceso_obj.pase_entrada_fields[campo]] = valor
    return answers


def campos_pase_completo(acceso_obj, dias_vigencia):
    """
    Campos de un pase con todo lo que pide access_pass_set_status: nombre,
    foto, identificación, fecha hasta, a quién visita y quién lo autorizó.
    Cada test quita o cambia solo lo que revisa.
    """
    return {
        "walkin_nombre": NOMBRE_PASE_UNIT,
        "walkin_fotografia": FOTO_VALIDA,
        "walkin_identificacion": IDENTIFICACION_VALIDA,
        "fecha_desde_hasta": fecha_hasta(acceso_obj, dias_vigencia),
        "grupo_visitados": [
            {de(acceso_obj, "CONF_AREA_EMPLEADOS_CAT_OBJ_ID").CONF_AREA_EMPLEADOS_CAT_OBJ_ID: {acceso_obj.mf["nombre_empleado"]: ANFITRION_PASE}}
        ],
        "catalago_autorizado_por": {acceso_obj.pase_entrada_fields["autorizado_por"]: AUTORIZADO_POR},
    }


def pase_nuevo(acceso_obj, dias_desde=DIAS_VIGENTE, **cambios):
    """+ Nuevo Pase desde web con fechas vigentes; cada test cambia solo lo que revisa."""
    pase = copy.deepcopy(PASE_NUEVO)
    pase["fecha_desde_visita"] = fecha_hasta(acceso_obj, dias_desde)
    pase["fecha_desde_hasta"] = fecha_hasta(acceso_obj, dias_desde + DIAS_VIGENTE)
    pase.update(cambios)
    return pase


def crear_pase_simulado(acceso_obj, mocker):
    """
    Simula lo que create_access_pass consulta fuera de la función (forma,
    usuario, QR, ubicaciones, anfitriones, invitación) para revisar solo sus
    validaciones; con de() el mock cae donde vive el método, en addons o en
    Sanic. Regresa el mock del guardado.
    """
    mocker.patch.object(acceso_obj.lkf_api, "get_metadata", return_value={})
    mocker.patch.object(acceso_obj.lkf_api, "get_user_by_id", return_value={"timezone": acceso_obj.user["timezone"]})
    mocker.patch("linkaform_api.generar_qr.LKF_QR")
    for metodo, valor in (
        ("get_requerimientos_ubicaciones", []),
        ("get_docs_pase_link", ""),
        ("access_pass_vista_a", []),
        ("get_locations_address", {}),
        ("get_areas_by_location", []),
        ("access_pass_create_ics", {}),
        ("autorizar_pase_acceso", {}),
    ):
        mocker.patch.object(de(acceso_obj, metodo), metodo, return_value=valor)
    return mocker.patch.object(acceso_obj.lkf_api, "post_forms_answers", return_value=dict(PASE_GUARDADO))
